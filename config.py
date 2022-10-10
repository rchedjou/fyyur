import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
# SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD")
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:{0}@localhost:5432/fyyurs'.format(DATABASE_PASSWORD)

