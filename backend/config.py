import os
basedir = os.path.abspath(os.path.dirname(__file__))

from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

def _parse_sentinel_url(url):
    """Return (single_sentinel_url, sentinels_list) from a semicolon-separated sentinel URL.

    urllib.parse cannot handle sentinel://h1:p1;h2:p2;h3:p3 — it treats
    '26379;h2:p2...' as the port and raises ValueError.  We split out the
    extra hosts and return them as a list of (host, port) tuples so they can
    be passed via transport_options['sentinels'] instead.
    """
    if not url or 'sentinel://' not in url:
        return url, None

    rest = url[len('sentinel://'):]
    # strip optional /db suffix
    db_suffix = ''
    if '/' in rest:
        hosts_part, db_part = rest.rsplit('/', 1)
        db_suffix = '/' + db_part
    else:
        hosts_part = rest

    sentinels = []
    for entry in hosts_part.split(';'):
        entry = entry.strip()
        if ':' in entry:
            host, port = entry.rsplit(':', 1)
            sentinels.append((host, int(port)))
        elif entry:
            sentinels.append((entry, 26379))

    if not sentinels:
        return url, None

    first_host, first_port = sentinels[0]
    single_url = f'sentinel://{first_host}:{first_port}{db_suffix}'
    return single_url, sentinels


class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY')
        SECURITY_PASSWORD_SALT = os.getenv("nemeltdavs")
        
        ZINC_SMALL_WORLD_SERVER = os.getenv('ZINC_SMALL_WORLD_SERVER') or "https://swp.docking.org"    
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

        ENV=os.getenv('ENV', 'production')

        _broker_url_raw = os.getenv('CELERY_BROKER_URL')
        _result_backend_raw = os.getenv('CELERY_RESULT_BACKEND')

        _broker_url, _broker_sentinels = _parse_sentinel_url(_broker_url_raw)
        _backend_url, _backend_sentinels = _parse_sentinel_url(_result_backend_raw)

        CELERY_BROKER_URL = _broker_url
        CELERY_RESULT_BACKEND = _backend_url

        _broker_transport_opts = {
            'master_name': 'cartblanche-master',
            'sentinel_kwargs': {},
        }
        if _broker_sentinels:
            _broker_transport_opts['sentinels'] = _broker_sentinels

        _backend_transport_opts = {
            'master_name': 'cartblanche-master',
            'sentinel_kwargs': {},
            'key_prefix': f'celery-task-{ENV}-',
        }
        if _backend_sentinels:
            _backend_transport_opts['sentinels'] = _backend_sentinels

        CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = _backend_transport_opts
        CELERY_BROKER_TRANSPORT_OPTIONS = _broker_transport_opts
        
    
        GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        BASE_URL = "https://cartblanche22.docking.org"
        SQLALCHEMY_BINDS = {
            # Server Database
            'zinc22_common': os.getenv('COMMON_DATABASE'),
            'zinc22': os.getenv('ZINC22_DATABASE'),
            'tin': os.getenv('TIN_DATABASE'),
            'zinc20': os.getenv('ZINC20_DATABASE'),
        }
        
        DOWNLOAD_PASS_2D = os.getenv('DOWNLOAD_PASS_2D')
        DOWNLOAD_USERNAME_2D = os.getenv('DOWNLOAD_USERNAME_2D')