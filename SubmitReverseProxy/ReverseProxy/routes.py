from typing import Tuple, Optional, Callable, Any
from functools import wraps
import logging
import os

from flask import Blueprint, Request, \
    request, current_app, \
    send_from_directory, g, \
    redirect
from flask_cors import cross_origin
from werkzeug.exceptions import BadRequest

from google.cloud.storage import Client
import google.auth
from google.auth.credentials import Credentials
from google.auth.transport import requests

from .authorize import authorize_user_for_submission
from .html_queries import get_source_format
from .poll import poll_submission
from .util import untar, clean_up
from .exceptions import AuthError, UnauthorizedError

blueprint = Blueprint('routes', __name__, '')

def _get_google_auth () -> Tuple[Credentials, str, Client]:
    credentials, project_id = google.auth.default()
    return (credentials, project_id, Client(credentials=credentials))

def _get_arxiv_user_id () -> int:
    try:
        return request.auth.user.user_id
    except Exception as e:
        raise AuthError from e

def authorize (submission_id: int):
    user_id = _get_arxiv_user_id()
    authorize_user_for_submission(user_id, submission_id)
    
@blueprint.route('/<int:submission_id>/poll', methods=['GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
# @authorize
def poll (submission_id: int):
    authorize(submission_id)
    return poll_submission(submission_id)

@blueprint.route('/<int:submission_id>/view', methods=['GET'])
@cross_origin(supports_credentials=True)
# @authorize
def get (submission_id: int):
    authorize(submission_id)

    BUCKET = current_app.config['CONVERTED_BUCKET_SUB_ID']
    TARS_DIR = current_app.config['TARS_DIR']

    _, _, storage_client = _get_google_auth()
    bucket = storage_client.get_bucket(BUCKET)
    blob = bucket.blob(f'{submission_id}.tar.gz')

    blob.download_to_filename(f'{TARS_DIR}{submission_id}')

    logging.info(f'Successfully downloaded to {TARS_DIR}{submission_id}')

    abs_path = untar(submission_id)
    dir = os.path.relpath(abs_path, current_app.root_path)

    logging.info(f'Successfully untarred to {abs_path}')
    
    return send_from_directory (dir, f'{submission_id}.html')

@blueprint.route('/<int:submission_id>/<path:path>', methods=['GET'])
@cross_origin(supports_credentials=True)
def get_static (submission_id: int, path: str):
    SITES_DIR = current_app.config['SITES_DIR']

    dir = os.path.join(
        os.path.relpath(SITES_DIR, current_app.root_path),
        str(submission_id)
    )

    return send_from_directory (dir, path)


@blueprint.app_errorhandler(BadRequest)
@cross_origin(supports_credentials=True)
def handle_bad_request(e):
    # TODO: 404 Page for submissions?
    logging.warning(f'Error: {e}')
    return 'Internal Server Error', 500

@blueprint.app_errorhandler(AuthError)
@cross_origin(supports_credentials=True)
def handle_auth_error(e):
    logging.warning(f'Error {e}')
    return 'You do not have access to this page', 403

@blueprint.app_errorhandler(AuthError)
@cross_origin(supports_credentials=True)
def handle_unauth_error(e):
    logging.warning(f'Error {e}')
    return 'You do not have access to this page', 403

@blueprint.app_errorhandler(500)
@cross_origin(supports_credentials=True)
def handle_500(e):
    # TODO: 404 Page for submissions?
    logging.warning(f'Error: {e}')
    return 'Internal Server Error', 500

@blueprint.app_errorhandler(404)
@cross_origin(supports_credentials=True)
def handle_404(e):
    # TODO: 404 Page for submissions?
    logging.warning(f'Error: {e}')
    return 'This page does not exist', 404
