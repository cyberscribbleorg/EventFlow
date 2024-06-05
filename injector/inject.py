import os
import gzip
import json
import logging
import sys
from datetime import datetime, timedelta
import requests
from upload2pg import insert_event_if_not_exist, connect_with_retry

# Configure logging
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Directories and tracking file
DOWNLOAD_FOLDER = '/data/downloads'
MISSED_FOLDER = '/data/error'
TRACKING_FILE = os.path.join(DOWNLOAD_FOLDER, 'harvest.track')

os.makedirs(MISSED_FOLDER, exist_ok=True)

# Global configuration dictionary
config = {}

def load_config():
    """Load configuration from config.json and environment variables."""
    global config
    with open('config.json', 'r') as file:
        config = json.load(file)

    # Override with environment variables if they exist
    config['db'] = os.getenv("DB_NAME", config.get('db', "Default PostgreSQL"))
    config['username'] = os.getenv("DB_USER", config.get('username', "user"))
    config['password'] = os.getenv("DB_PASS", config.get('password', "password"))
    config['host'] = os.getenv("DB_HOST", config.get('host', "localhost"))
    config['port'] = os.getenv("DB_PORT", config.get('port', "5432"))
    print(config)

def filter_event(event):
    """Filter event based on config criteria."""
    users = config.get('users', [])
    projects = config.get('projects', [])

    actor = event['actor']['login']
    repo_name = event['repo']['name']

    if users and actor in users:
        return True
    if projects and repo_name in projects:
        return True

    return False   


def process_json_file(file_path, conn):
    """Process a JSON file and insert events into the database."""
    processed_count = 0
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if not lines:
                logging.warning(f"Empty file..skipping..: {file_path}")
                return False

            events = [json.loads(line.strip()) for line in lines]

            for event in events:
                if filter_event(event):
                    insert_event_if_not_exist(conn, event)
                    processed_count += 1
            logging.info(f"Processed count {processed_count}")
            return True
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error in file {file_path}: {e}")
    except IOError as e:
        logging.error(f"IO error while reading file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing file {file_path}: {e}")

    return False


def extract_and_process_file(file_name, conn):
    """Extract a gzipped file and process its contents."""
    gz_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    json_path = gz_path[:-3]  # Remove '.gz' to get the '.json' path

    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(json_path, 'wb') as f_out:
                f_out.write(f_in.read())
        logging.info(f"Extracted {gz_path} to {json_path}")

        if process_json_file(json_path, conn):
            os.remove(gz_path)
            os.remove(json_path)
            logging.info(f"Deleted {gz_path} and {json_path}")
        else:
            os.rename(gz_path, os.path.join(MISSED_FOLDER, file_name))
            os.rename(json_path, os.path.join(MISSED_FOLDER, os.path.basename(json_path)))
            logging.info(f"Moved {gz_path} and {json_path} to {MISSED_FOLDER}")

    except Exception as e:
        logging.error(f"Failed to process {file_name}: {str(e)}")
        if os.path.exists(gz_path):
            os.rename(gz_path, os.path.join(MISSED_FOLDER, file_name))
        if os.path.exists(json_path):
            os.rename(json_path, os.path.join(MISSED_FOLDER, os.path.basename(json_path)))
        logging.info(f"Moved {gz_path} and {json_path} to {MISSED_FOLDER} due to error")


def get_last_downloaded():
    """Retrieve the last downloaded datetime from the tracking file."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as file:
            last_downloaded = file.read().strip()
        if last_downloaded:
            return datetime.strptime(last_downloaded, '%Y-%m-%d-%H')
    return None


def update_last_downloaded(dt):
    """Update the tracking file with the last downloaded datetime."""
    with open(TRACKING_FILE, 'w') as file:
        file.write(dt.strftime('%Y-%m-%d-%H'))


def do_harvest_and_inject(conn):
    """Download and process event data files from GitHub Archive."""
    global config
    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
    delta = timedelta(days=1)

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'w') as file:
            file.write('')

    last_downloaded_dt = get_last_downloaded()
    if last_downloaded_dt:
        start_date = last_downloaded_dt + timedelta(hours=1)

    current_date = start_date
    while current_date <= end_date:
        for hour in range(24):
            file_name = f"{current_date.strftime('%Y-%m-%d')}-{hour}.json.gz"
            file_path = os.path.join(DOWNLOAD_FOLDER, file_name)
            url = f"https://data.gharchive.org/{file_name}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    update_last_downloaded(current_date.replace(hour=hour))
                    logging.info(f"Successfully downloaded {file_name}")
                    extract_and_process_file(file_path, conn)
                else:
                    logging.warning(f"Failed to download {file_name}, status code {response.status_code}")
            except Exception as e:
                logging.error(f"Error downloading {file_name}: {str(e)}")
        current_date += delta


if __name__ == "__main__":
    logging.info("Starting the injector service...")
    load_config()
    conn = connect_with_retry(config)
    if conn:
        logging.info("Connected successfully...")
        do_harvest_and_inject(conn)
    logging.info("Injector service exiting...")