import os
basedir = os.path.abspath(os.path.dirname(__file__))

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SECURITY_PASSWORD_SALT = os.getenv("nemeltdavs")
        
        ZINC_SMALL_WORLD_SERVER = os.getenv('ZINC_SMALL_WORLD_SERVER') or "http://swp.docking.org"    
        TEMPLATES_AUTO_RELOAD = True

        SQLALCHEMY_TRACK_MODIFICATIONS = False
        MAIL_SERVER =  os.getenv('MAIL_SERVER')
        MAIL_PORT = 587 or int(os.getenv('MAIL_PORT'))
        MAIL_USE_TLS = 1 or os.getenv('MAIL_USE_TLS') is not None
        MAIL_USERNAME = os.getenv('MAIL_USERNAME')
        MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
        MAIL_DEFAULT_SENDER = os.getenv('MAIL_USERNAME')
        ADMINS = [os.getenv('MAIL_USERNAME')]

        CELERY_IMPORTS = ("app.data.tasks.search_zinc", "app.data.tasks.search_smiles", "app.data.tasks.get_random" )
        SMALLWORLD_JAR_PATH = os.getenv("SMALLWORLD_JAR_PATH")
        SMALLWORLD_PUBLIC_MAP_PATH = os.getenv("SMALLWORLD_PUBLIC_MAP_PATH")
        SMALLWORLD_MAP_PATH = os.getenv("SMALLWORLD_MAP_PATH")
        SWDIR = os.getenv("SWDIR")
       
        CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
        CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND') or 'redis://0.0.0.0:6379/0'
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        SQLALCHEMY_BINDS = {
            # Server Database

            'zinc22_common': os.getenv('COMMON_DATABASE'),
            'zinc22': os.getenv('ZINC22_DATABASE'),
            'tin': os.getenv('TIN_DATABASE'),
            'zinc20': os.getenv('ZINC20_DATABASE'),
        }

        DOWNLOAD_PASS_2D = os.getenv('DOWNLOAD_PASS_2D')
        DOWNLOAD_USERNAME_2D = os.getenv('DOWNLOAD_USERNAME_2D')


        
