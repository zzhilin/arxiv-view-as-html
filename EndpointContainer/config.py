import os

CLASSIC_SESSION_HASH = os.environ.get('CLASSIC_SESSION_HASH')

CLASSIC_DATABASE_URI = os.environ.get('CLASSIC_DATABASE_URI')
"""If not set, legacy database integrations will not be available."""

SQLALCHEMY_DATABASE_URI = CLASSIC_DATABASE_URI
# uncomment this
# SQLALCHEMY_DATABASE_URI = "mysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam"

STATIC_FOLDER = '/templates'
TEMPLATE_FOLDER = '/templates'