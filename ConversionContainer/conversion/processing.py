"""Module that handles the conversion process from LaTeX to HTML"""
import tarfile
import os
import re
import subprocess
import shutil
from typing import Any, Tuple, Dict
import logging

from .config import (
    OUT_BUCKET_ARXIV_ID,
    OUT_BUCKET_SUB_ID,
    QA_BUCKET_NAME
)
from .util import get_google_storage_client
from .models.db import db
from .exceptions import *
from .concurrency_control import \
    write_start, write_success
from .addons import inject_addons, copy_static_assets



# Change such that we can handle multiple requests
# Raise max requests allowed on cloud run
# Error handling try/catch - send event maybe


def process(payload: Dict[str, str]) -> bool:
    """
    Runs latexml on the blob in the payload and uploads
    the results to the output bucket in the config
    file.

    Parameters
    ----------
    payload : JSON
        https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/storage/v1/data.proto

    Returns
    -------
    Boolean
        Returns true unless an exception occurs

    Raises
    ------
    Exception
        'PayloadError': No submission id (payload.name)
            contained in the payload. Likely the entire
            payload is invalid/malformed.
    """
    try:
        doc_type = 'doc' if payload['bucket'] == 'latexml_arxiv_id_source' else 'sub'
        logging.info(f'BUCKET: {payload["bucket"]}')
        payload_name = payload.get('name')
        if payload_name:
            pass
        else:
            raise PayloadError('No name identifier')
        
        # Check file format and download to ./[tar]
        logging.info(f"Step 1: Download {payload['name']}")
        tar, id = get_file(payload)

        # Write to DB that process has started
        logging.info(f"Write start process to db")
        write_start(id, tar, doc_type)

        # Untar file ./[tar] to ./extracted/id/
        logging.info(f"Step 2: Untar {id}")
        source = untar(tar, id)

        # Remove .ltxml files from [source] (./extracted/id/)
        logging.info(f"Step 3: Remove .ltxml for {id}")
        remove_ltxml(source)

        # Identify main .tex source in [source]
        logging.info(f"Step 4: Identify main .tex source for {id}")
        main = find_main_tex_source(source)

        # ./extracted/id/html/ will hold the exact tree
        # that we will ultimately upload to gcs
        bucket_path = os.path.join(source, 'html')
        out_path = os.path.join(bucket_path, id)
        try:
            os.makedirs(out_path)
        except FileExistsError:
            # Abort if this fails:
            shutil.rmtree(bucket_path)
            os.makedirs(out_path)
            
        # Run LaTeXML on main and output to ./extracted/id/html/id
        logging.info(f"Step 5: Do LaTeXML for {id}")
        do_latexml(main, os.path.join(out_path, id), id)

        # Post process html
        logging.info(f"Step 6: Upload html for {id}")
        post_process(bucket_path, id)
        
        logging.info(f"Step 7: Upload html for {id}")
        tar, id = get_file(payload)

        if doc_type == 'doc':
            upload_dir_to_gcs(bucket_path, OUT_BUCKET_ARXIV_ID)
        else:
            upload_tar_to_gcs(id, bucket_path, OUT_BUCKET_SUB_ID, f'{bucket_path}/{id}.tar.gz')
        write_success(id, tar, doc_type)
        logging.info(f"{id} uploaded successfully!") 
        # db.write_success(payload_name)
    except Exception as e:
        logging.info(f'Conversion unsuccessful with {e}')
        # TODO: db Write failure
        # if payload.get('name'):
        #     db.write_failure(payload['name'])
        # else:
        #     pass
            # what to do if we got a bad submission_id?
    finally:
        if 'out_path' in locals() and \
            'tar' in locals() and \
            'id' in locals():
            try:
                clean_up(tar, id)
            except Exception as e:
                logging.info(f"Failed to clean up {id} with {e}")
    return True

def _unwrap_payload (payload_name: str) -> Tuple[str, str]:
    fname = payload_name.split('/')[1]
    idv = fname.replace('.tar.gz', '')
    return fname, idv

def get_file(payload: dict[str, Any]) -> Tuple[str, str]:
    """
    Checks if the payload contains a .tar.gz file
    and if so it downloads the file to "fpath".
    Otherwise, it throws an Exception, ending the process
    and logging the non .tar.gz file.

    Parameters
    ----------
    payload : dict[str, Any]
        https://github.com/googleapis/google-cloudevents/blob/main/proto/google/events/cloud/storage/v1/data.proto

    Returns
    -------
    fpath : str
        File path to the .tar.gz object
    """
    if payload['name'].endswith('.gz'):
        fname, id = _unwrap_payload(payload['name'])
        try:
            os.remove(f"./{fname}")
        except:
            pass
    else:
        raise FileTypeError(f"{payload['name']} was not a .tar.gz")
    try:
        blob = get_google_storage_client().bucket(payload['bucket']) \
            .blob(payload['name'])
        with open(fname, 'wb') as read_stream:
            blob.download_to_file(read_stream)
            read_stream.close()
        return os.path.abspath(f"./{fname}"), id
    except Exception as exc:
        raise GCPBlobError(
            f"Download of {payload['name']} from {payload['bucket']} failed") from exc


def untar(fpath: str, dir_name: str) -> str:
    """
    Extracts the .tar.gz at "fpath" into directory
    "dir_name".

    Parameters
    ----------
    fpath : str
        File path to the .tar.gz object
    dir_name : str
        Name that we want to give to the directory
        that contains the extracted files

    Returns
    -------
    extracted_directory : str
        File path of the directory that contains the
        extracted files
    """
    try:
        with tarfile.open(fpath) as tar:
            # Assuming they protect us from files with ../ or / in the name
            tar.extractall(f"extracted/{dir_name}")
            tar.close()
        return os.path.abspath(f"extracted/{dir_name}")
    except Exception as exc:
        raise TarError(
            f"Tarfile at {fpath} failed to extract in untar()") from exc


def remove_ltxml(path: str) -> None:
    """
    Remove files with the .ltxml extension from the
    directory "path".

    Parameters
    ----------
    path : str
        File path to the directory containing unzipped .tex source
    """
    try:
        for root, _, files in os.walk(path):
            for file in files:
                if str(file).endswith('.ltxml'):
                    os.remove(os.path.join(root, file))
    except Exception as exc:
        raise LaTeXMLRemoveError(
            f".ltxml file at {path} failed to be removed") from exc


def find_main_tex_source(path: str) -> str:
    """
    Looks inside the directory at "path" and determines the
    main .tex source. Assumes that the main .tex file
    must start with "documentclass". To account for
    common Overleaf templates that have multiple .tex
    files that start with "documentclass", assumes that
    the main .tex file is not of class "standalone"
    or "subfiles".

    Parameters
    ----------
    path : str
        File path to a directory containing unzipped .tex source

    Returns
    -------
    main_tex_source : str
        File path to the main .tex source in the directory
    """
    try:
        tex_files = [f for f in os.listdir(path) if f.endswith('.tex')]
        if len(tex_files) == 1:
            return os.path.join(path, tex_files[0])
            # Returns the only .tex file in the source files
        else:
            main_files = {}
            for tf in tex_files:
                with open(os.path.join(path, tf), "r") as file:
                    for line in file:
                        if re.search(r"^\s*\\document(?:style|class)", line):
                            # https://arxiv.org/help/faq/mistakes#wrongtex
                            # according to this page, there should only be one tex file with a \documentclass
                            if tf in ["paper.tex", "main.tex", "ms.tex", "article.tex"]:
                                main_files[tf] = 1
                            else:
                                main_files[tf] = 0
                            break
            if len(main_files) == 1:
                return (os.path.join(path, list(main_files)[0]))
            elif len(main_files) == 0:
                raise MainTeXError(
                    f"No main .tex found file in {path}")
            else:
                # account for the two main ways of creating multi-file
                # submissions on overleaf (standalone, subfiles)
                for mf in main_files:
                    with open(os.path.join(path, mf), "r") as file:
                        for line in file:
                            if re.search(r"^\s*\\document(?:style|class).*(?:\{standalone\}|\{subfiles\})", line):
                                main_files[mf] = -99999
                                break
                                # document class of main should not be standalone or subfiles
                                # #the main file is just {article} or something else
                return (os.path.join(path, max(main_files, key=main_files.__getitem__)))
    except Exception as exc:
        raise MainTeXError(
            f"Process to find main .tex file in {path} failed") from exc


def do_latexml(main_fpath: str, out_dpath: str, sub_id: str) -> None:
    """
    Runs latexml on the .tex file at main_fpath and
    outputs the html at out_fpath.

    Parameters
    ----------
    main_fpath : str
        Main .tex file path
    out_dpath : str
        Output directory file path
    sub_id: str
        submission id of the article
    """
    latexml_config = ["latexmlc",
                      "--preload=[nobibtex,ids,localrawstyles,mathlexemes,magnify=2,zoomout=2,tokenlimit=99999999,iflimit=1499999,absorblimit=1299999,pushbacklimit=599999]latexml.sty",
                      "--path=/opt/arxmliv-bindings/bindings",
                      "--path=/opt/arxmliv-bindings/supported_originals",
                      "--pmml", "--cmml", "--mathtex",
                      "--timeout=2700",
                      "--nodefaultresources",
                      "--css=css/ar5iv.min.css",
                      f"--source={main_fpath}", f"--dest={out_dpath}.html"]
    completed_process = subprocess.run(
        latexml_config,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        text=True)
    errpath = os.path.join(os.getcwd(), f"{sub_id}_stdout.txt")
    with open(errpath, "w") as f:
        f.write(completed_process.stdout)
    try:
        bucket = get_google_storage_client().bucket(QA_BUCKET_NAME)
        errblob = bucket.blob(f"{sub_id}_stdout.txt")
        errblob.upload_from_filename(f"{sub_id}_stdout.txt")
    except Exception as exc:
        raise GCPBlobError(
            f"Uploading {sub_id}_stdout.txt to {QA_BUCKET_NAME} failed in do_latexml") from exc
    os.remove(errpath)

def post_process (src_dir: str, id: str):
    """
    Adds the arxiv overlay to the latexml output. This
    includes injecting html and moving static assets

    Parameters
    ----------
    src_dir : str
        path to the directory to be uploaded. This should be 
        in the form of ./extracted/{id}/html/
    bucket_name : str
        submission_id for submissions and paper_id for 
        published documents
    """
    inject_addons(os.path.join(src_dir, f'{id}/{id}.html'), id)
    copy_static_assets(os.path.join(src_dir, str(id)))


def upload_dir_to_gcs (src_dir: str, bucket_name: str):
    """
    Uploads the directory subtree of the given directory to the 
    given GCS bucket

    Parameters
    ----------
    src_dir : str
        path to the directory to be uploaded. This should be 
        in the form of ./extracted/{id}/html/
    bucket_name : str
        name of bucket to upload to
    """
    bucket = get_google_storage_client().bucket(bucket_name)
    for root, _, fnames in os.walk(src_dir):
        for fname in fnames:
            abs_fpath = os.path.join(root, fname)
            logging.info(f'uploading {os.path.relpath(abs_fpath, src_dir)}')
            bucket.blob(
                os.path.relpath(
                    abs_fpath,
                    src_dir
                )
            ) \
            .upload_from_filename(abs_fpath)

def upload_tar_to_gcs (sub_id: int, src_dir: str, bucket_name: str, destination_fname: str) -> None:
    """
    Uploads a .tar.gz object named {destination_fname}
    containing a folder called "html" located at {path}
    to the bucket named {bucket_name}. 

    Parameters
    ----------
    path : str
        Directory path in format /.../.../sub_id/html
        containing the static files for ar        # Read and update hash in chunks of 4K
the object to.
    destination_fname : str
        What to name the .tar.gz object, should be the
        submission id.
    """
    with tarfile.open(destination_fname, "w:gz") as tar:
        tar.add(f'{src_dir}/{sub_id}', arcname=str(sub_id))
    bucket = get_google_storage_client().bucket(bucket_name)
    blob = bucket.blob(f'{sub_id}.tar.gz')
    blob.upload_from_filename(destination_fname)
    
def clean_up (tar, id):
    os.remove(tar)
    shutil.rmtree(f'extracted/{id}')
