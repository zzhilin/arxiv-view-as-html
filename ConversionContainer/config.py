"""Config that specifies output bucket name for uploading converted articles"""

import os

IN_BUCKET_ARXIV_ID = 'latexml_arxiv_id_source'
OUT_BUCKET_ARXIV_ID = 'latexml_arxiv_id_converted'
OUT_BUCKET_SUB_ID = 'latexml_submission_converted'
QA_BUCKET_NAME = 'latexml_qa'

LATEXML_DB_URI = os.environ.get('LATEXML_DB_URI')
