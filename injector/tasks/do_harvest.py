from celery_app import app
import logging
import os
import requests
from datetime import datetime, timedelta
from utils import load_config, get_download_folder, get_download_limit
import time

from tasks.do_extract import do_extract


DOWNLOAD_FOLDER = get_download_folder()
TRACKING_FILE = os.path.join(DOWNLOAD_FOLDER, 'harvest.track')

@app.task(bind=True)
def do_harvest(self):
    config = load_config()

    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
    delta = timedelta(days=1)

    try:
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
        logging.info(f"Directory {DOWNLOAD_FOLDER} created successfully or already exists.")
    except OSError as e:
        logging.error(f"Error creating directory {DOWNLOAD_FOLDER}: {e}")
        return
    
    if not os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'w') as file:
            file.write('')

    last_downloaded_dt = get_last_downloaded(TRACKING_FILE)
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
                    update_last_downloaded(current_date.replace(hour=hour), TRACKING_FILE)
                    logging.info(f"Successfully downloaded {file_name}")
                    do_extract.delay(file_name)

                while True:
                    num_files = len([name for name in os.listdir(DOWNLOAD_FOLDER) if os.path.isfile(os.path.join(DOWNLOAD_FOLDER, name))])
                    if num_files >= int(get_download_limit()):
                        logging.info(f"{get_download_limit()} files downloaded. Sleeping for 30 seconds.")
                        time.sleep(30)  # Sleep for 30 seconds
                    else:
                        break 

                else:
                    logging.warning(f"Failed to download {file_name}, status code {response.status_code}")
            except Exception as e:
                logging.error(f"Error downloading {file_name}: {str(e)}")
        current_date += delta

def get_last_downloaded(tracking_file):
    """Retrieve the last downloaded datetime from the tracking file."""
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as file:
            last_downloaded = file.read().strip()
        if last_downloaded:
            return datetime.strptime(last_downloaded, '%Y-%m-%d-%H')
    return None

def update_last_downloaded(dt, tracking_file):
    """Update the tracking file with the last downloaded datetime."""
    with open(tracking_file, 'w') as file:
        file.write(dt.strftime('%Y-%m-%d-%H'))