import pytest
import shutil
from unittest.mock import MagicMock
import os
from ..convert import (
    untar,
    remove_ltxml,
    _clean_up,
    _post_process,
    do_latexml,
    find_main_tex_source
)
from ..exceptions import FileTypeError

@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)

@pytest.fixture(autouse=True)
def mock_google_storage_client (mocker):
    mocker.patch('source.buckets.util.get_google_storage_client', 
                 return_value=MagicMock())
    
@pytest.fixture 
def payload_arxiv_id (): return {'name': '2012.02205/2012.02205.tar.gz', 'bucket': 'latexml_arxiv_id_source'}
@pytest.fixture
def payload_sub_id (): return {'name': '3966840/3966840.tar.gz', 'bucket': 'latexml_submission_source'}
@pytest.fixture
def payload_bad (): return {'name': '3966840/source.log', 'bucket': 'latexml_submission_source'}

"""
******************************
********  untar tests  *******
******************************
"""

@pytest.mark.processing_unit_tests
def test_untar_success1 ():
    os.chdir('ancillary_files')
    assert os.path.exists('2012.02205.tar'), \
        'This test depends on tests/ancillary_files/2012.02205.tar'
    assert not os.path.exists('extracted/2012.02205'), \
        'This test will always success unless ancillary_files/extracted '\
        'is emptied/cleaned'
    untar ('2012.02205.tar', 'extracted/2012.02205')
    assert os.path.exists('extracted/2012.02205'), \
        'Failed to extract the tar to tests/ancillary_files/extracted/2012.02205'
    shutil.rmtree('extracted')
    
@pytest.mark.processing_unit_tests
def test_untar_success2 ():
    os.chdir('ancillary_files')
    assert os.path.exists('3966840.tar'), \
        'This test depends on tests/ancillary_files/3966840.tar'
    assert not os.path.exists('extracted/3966840.tar'), \
        'This test will always success unless ancillary_files/extracted '\
        'is emptied/cleaned'
    untar ('3966840.tar', 'extracted/3966840')
    assert os.path.exists('extracted/3966840'), \
        'Failed to extract the tar to tests/ancillary_files/extracted/3966840'
    shutil.rmtree('extracted')
    

"""
******************************
****  remove_ltxml tests  ****
******************************
"""

@pytest.mark.processing_unit_tests
def test_remove_ltxml_true_pos ():
    os.chdir('ancillary_files')
    assert os.path.exists('malicious.ltxml'), \
        'This test depends on tests/ancillary_files/malicious.ltxml'
    assert os.path.exists('./ltxml'), \
        'This test depends on tests/ancillary_files/ltxml'
    shutil.copy('malicious.ltxml', 'ltxml/malicious.ltxml')
    remove_ltxml('ltxml')
    assert not os.path.exists('./ltxml/malicious.ltxml'), \
        'Failed to remove malicious.ltxml from tests/ancillary_files/ltxml'

@pytest.mark.processing_unit_tests
def test_remove_ltxml_true_neg ():
    os.chdir('ancillary_files')
    assert os.path.exists('ltxml/non_malicious.tar.gz'), \
        'This test depends on tests/ancillary_files/ltxml/non_malicious.tar.gz'
    remove_ltxml('ltxml')
    assert os.path.exists('./ltxml/non_malicious.tar.gz'), \
        'Erroneously removed non_malicious.ltxml from tests/ancillary_files/ltxml'



"""
******************************
* find_main_tex_source tests *
******************************
"""

@pytest.mark.processing_unit_tests
def test_find_main_tex_source_single_source ():
    os.chdir('ancillary_files')
    assert os.path.exists('single_tex'), \
        'This test depends on tests/ancillary_files/single_tex'
    main_tex = find_main_tex_source ('single_tex') 
    assert main_tex == 'single_tex/main.tex', \
        f'Failed to indetify main tex file \'main.tex\' in \
        tests/ancillary_files/single_tex. Identified {main_tex} instead'

@pytest.mark.processing_unit_tests
def test_find_main_text_source_multiple_sources ():
    os.chdir('ancillary_files')
    assert os.path.exists('multiple_tex'), \
        'This test depends on tests/ancillary_files/multiple_tex'
    main_tex = find_main_tex_source ('multiple_tex') 
    assert main_tex == 'multiple_tex/paper.tex', \
        f'Failed to indetify main tex file \'paper.tex\' in \
        tests/ancillary_files/paper_tex. Identified {main_tex} instead'



"""
******************************
****** do_latexml tests ******
******************************
"""

# TODO: This just runs a subprocess and uploads to a bucket.
#       We just mock the bucket and the subprocess isn't 
#       written by us, so I'm skipping this for now


"""
******************************
****  upload_output tests ****
******************************
"""

# TODO: This will also just be mostly mocked. 