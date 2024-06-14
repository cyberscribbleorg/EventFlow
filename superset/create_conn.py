import requests
import json
import os
import logging
from superset_client import SupersetClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

admin_username = os.getenv('SUPERSET_ADMIN_USER', 'admin')
admin_password = os.getenv('SUPERSET_ADMIN_PASSWORD', 'admin')

superset_host = os.getenv('SUPERSET_HOST', '127.0.0.1')
superset_port = os.getenv('SUPERSET_PORT', '8088')
superset_url = f'http://{superset_host}:{superset_port}'

db_name = os.getenv('DB_NAME', 'mydatabase')
db_user = os.getenv('DB_USER', 'myuser')
db_password = os.getenv('DB_PASS', 'mypassword')
db_host = os.getenv('DB_HOST', 'db')
db_port = os.getenv('DB_PORT', '5432')

if __name__ == '__main__':
    try:
        client = SupersetClient(superset_url, admin_username, admin_password)

        connection_payload = {
            'configuration_method': 'sqlalchemy_form',
            'database_name': db_name,
            'driver': 'postgresql',
            'engine': 'postgresql',
            'extra': json.dumps({
                'metadata_params': {},
                'engine_params': {},
                'metadata_cache_timeout': {},
                'schemas_allowed_for_csv_upload': [],
            }),
            'sqlalchemy_uri': f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}',
            'parameters': {},
            'impersonate_user': False
        }

        db_id = client.check_db_connection_exists(db_name)
        if db_id:
            client.test_db_connection(connection_payload)
        else:
            db_id = client.create_db_connection(connection_payload)
            if db_id:
                client.test_db_connection(connection_payload)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
