import requests

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
    """ Create a new database connection using the session with CSRF token """
    db_url = f"{base_url}/api/v1/database/"
    db_payload = {
        "database_name": "Default PostgreSQL",
        "sqlalchemy_uri": "postgresql://user:password@localhost:5432/mydatabase",
        "extras": "{\"metadata_params\":{},\"engine_params\":{},\"metadata_cache_timeout\": {},\"schemas_allowed_for_csv_upload\": []}"
    }
    response = session.post(db_url, json=db_payload)
    print(response.text)

if __name__ == "__main__":
    base_url = "http://localhost:8088"
    username = "admin"
    password = "admin"
    session = login(base_url, username, password)
    create_database(session, base_url)