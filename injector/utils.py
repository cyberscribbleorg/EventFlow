# utils.py
import os
import json

def load_config():
    """Load configuration from config.json and environment variables."""
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Override with environment variables if they exist
    config['db'] = os.getenv("DB_NAME", config.get('db', "Default PostgreSQL"))
    config['username'] = os.getenv("DB_USER", config.get('username', "user"))
    config['password'] = os.getenv("DB_PASS", config.get('password', "password"))
    config['host'] = os.getenv("DB_HOST", config.get('host', "localhost"))
    config['port'] = os.getenv("DB_PORT", config.get('port', "5432"))
    
    return config