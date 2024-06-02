import requests
import os

def get_csrf_token(session, base_url):
    """ Get CSRF token from Superset """
    response = session.get(f"{base_url}/api/v1/security/csrf_token/")
    response.raise_for_status()
    return response.json()["result"]

def login(base_url, username, password):
    session = requests.Session()
    login_url = f"{base_url}/api/v1/security/login"
    login_payload = {
        "username": username,
        "password": password,
        "provider": "db"
    }
    login_response = session.post(login_url, json=login_payload)
    login_response.raise_for_status()
    print("Login Response:", login_response.json())

    # Assuming bearer token is used and returned in login response
    access_token = login_response.json().get('access_token')
    if access_token:
        session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        })

    csrf_token = get_csrf_token(session, base_url)
    session.headers.update({
        "X-CSRFToken": csrf_token
    })
    return session

def create_database(session, base_url):
    # Fetch environment variables
    db_name = os.getenv("DB_NAME", "Default PostgreSQL")
    db_user = os.getenv("DB_USER", "user")
    db_password = os.getenv("DB_PASS", "password")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_database = os.getenv("DB_NAME", "mydatabase")
    
    sqlalchemy_uri = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_database}"

    # Check if the database already exists
    existing_dbs = session.get(f"{base_url}/api/v1/database/").json()
    if any(db['database_name'] == db_name for db in existing_dbs.get('result', [])):
        print("Database already exists.")
        return

    # Payload for creating a new database
    db_payload = {
        "database_name": db_name,
        "sqlalchemy_uri": sqlalchemy_uri,
        "extras": "{\"metadata_params\":{},\"engine_params\":{},\"metadata_cache_timeout\": {},\"schemas_allowed_for_csv_upload\": []}"
    }

    # Create the database if it does not exist
    response = session.post(f"{base_url}/api/v1/database/", json=db_payload)
    print(response.text)

if __name__ == "__main__":
    base_url = "http://localhost:8088"
    username = "admin"
    password = "admin"
    session = login(base_url, username, password)
    create_database(session, base_url)