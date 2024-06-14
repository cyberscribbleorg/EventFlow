import requests
import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SupersetClient:
    def __init__(self, superset_url, username, password):
        self.superset_url = superset_url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def get_csrf_token(self):
        response = self.session.get(f"{self.superset_url}/api/v1/security/csrf_token/")
        response.raise_for_status()
        return response.json()["result"]

    def get_auth_session(self):
        auth_endpoint = f'{self.superset_url}/api/v1/security/login'
        auth_payload = {
            "username": self.username,
            "password": self.password,
            "provider": "db"
        }
        headers = {'Content-Type': 'application/json'}
        try:
            response = self.session.post(auth_endpoint, json=auth_payload, headers=headers)
            response.raise_for_status()
            logger.info("Authentication successful")
            access_token = response.json().get('access_token')
            if access_token:
                self.session.headers.update({
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                })

            csrf_token = self.get_csrf_token()
            self.session.headers.update({
                "X-CSRFToken": csrf_token
            })
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication failed: {e}")
            logger.error(f"Response content: {response.content}")
            raise

    def check_db_connection_exists(self, db_name):
        db_endpoint = f'{self.superset_url}/api/v1/database/'
        try:
            if self.get_auth_session():
                response = self.session.get(db_endpoint)
                response.raise_for_status()
                databases = response.json().get('result', [])
                for db in databases:
                    if db['database_name'] == db_name:
                        logger.info(f"Database connection '{db_name}' already exists.")
                        return db['id']
            else:
                logger.error("Authentication session could not be established.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check database connections: {e}")
            logger.error(f"Response content: {response.content}")
            raise
        return None

    def create_db_connection(self, connection_payload):
        db_endpoint = f'{self.superset_url}/api/v1/database/'
        try:
            if self.get_auth_session():
                response = self.session.post(db_endpoint, json=connection_payload)
                response.raise_for_status()
                logger.info("Database connection created successfully")
                return response.json()['id']
            else:
                logger.error("Authentication session could not be established.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to create database connection: {e}")
            logger.error(f"Response content: {response.content}")
            raise

    def test_db_connection(self, connection_payload):
        test_endpoint = f'{self.superset_url}/api/v1/database/test_connection/'
        try:
            response = self.session.post(test_endpoint, json=connection_payload)
            response.raise_for_status()
            logger.info("Database connection is successful.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to test database connection: {e}")
            logger.error(f"Response content: {response.content}")
            raise


