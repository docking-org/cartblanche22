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
        MAIL_SERVER = 'smtp.googlemail.com' or os.getenv('MAIL_SERVER')
        MAIL_PORT = 587 or int(os.getenv('MAIL_PORT'))
        MAIL_USE_TLS = 1 or os.getenv('MAIL_USE_TLS') is not None
        MAIL_USERNAME = 'cartblanche20@gmail.com' or os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = 'molecule20' or os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
        ADMINS = [os.getenv('MAIL_USERNAME')]
