"""Initializes the Flask app"""
from conversion.factory import create_web_app
from conversion.models.util import create_all, drop_all, transaction
from conversion.util import get_google_logging_client

_ = get_google_logging_client()

app = create_web_app()
with app.app_context():
    with transaction():
        create_all() # Create table if it doesn't exist

if __name__=='__main__':
    app.run(debug=False)
