import os
basedir = os.path.abspath(os.path.dirname(__file__))

from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
        SECURITY_PASSWORD_SALT = os.getenv("nemeltdavs")
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI_LOCAL_ZINC22")
        TIN_URL = "10.20.1.17:5437"
        # TIN_URL = "localhost:6537"

        SQLALCHEMY_TRACK_MODIFICATIONS = False
        MAIL_SERVER = os.getenv('MAIL_SERVER')
        MAIL_PORT = int(os.getenv('MAIL_PORT') or 25)
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
        ADMINS = [os.getenv('MAIL_USERNAME')]
