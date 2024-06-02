import os

DB_USER = os.getenv('DB_USER', 'defaultuser')
DB_PASS = os.getenv('DB_PASS', 'defaultpassword')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')
DB_NAME = os.getenv('DB_NAME', 'defaultdb')

SQLALCHEMY_DATABASE_URI = f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24))  # Use a fixed value from an environment variable
SQLALCHEMY_POOL_RECYCLE = 1800
SQLALCHEMY_POOL_TIMEOUT = 120
AUTH_TYPE = 1
ROW_LEVEL_SECURITY = False
SQLLAB_ASYNC_TIME_LIMIT_SEC = 7200
APP_NAME = "Superset"
PUBLIC_ROLE_LIKE_GAMMA = True