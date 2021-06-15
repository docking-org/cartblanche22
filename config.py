import os
basedir = os.path.abspath(os.path.dirname(__file__))

from os.path import join, dirname
# from dotenv import load_dotenv
#
# dotenv_path = join(dirname(__file__), '.env')
# load_dotenv(dotenv_path)


class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
        SECURITY_PASSWORD_SALT = os.getenv("nemeltdavs")
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
        # SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI_LOCAL_ZINC22")
        ZINC_SMALL_WORLD_SERVER = "http://10.20.0.5:8080"
        # ZINC_SMALL_WORLD_SERVER = "http://swp.docking.org"

        SQLALCHEMY_TRACK_MODIFICATIONS = False
        MAIL_SERVER = os.getenv('MAIL_SERVER') or 'smtp.googlemail.com'
        MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
        MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') is not None or 1
        MAIL_USERNAME = os.getenv('MAIL_USERNAME') or 'cartblanche20@gmail.com'
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD') or 'molecule20'
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
        ADMINS = [os.getenv('MAIL_USERNAME')]
