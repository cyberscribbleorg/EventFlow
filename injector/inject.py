import os
import gzip
import json
import time
import logging
import sys
from datetime import datetime, timedelta
import time
import requests

# Setup logging
#logging.basicConfig(filename='consumer.log', level=logging.INFO,
#                   format='%(asctime)s:%(levelname)s:%(message)s')
logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

download_folder = '/data/downloads'
missed_folder = '/data/error'
tracking_file = os.path.join(download_folder, 'harvest.track')

os.makedirs(missed_folder, exist_ok=True)


def process_json_file(file_path):
    processed_count = 0
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if not lines:
                logging.warning(f"Empty file..skipping..: {file_path}")
                return False

            events = []
            for line in lines:
                events += [json.loads(line.strip())]

            for event in events:
                #insert_event_if_not_exist(conn, event) //TODO
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

def extract_and_process_file(file_name):
    gz_path = os.path.join(download_folder, file_name)
    json_path = gz_path[:-3]  # Remove '.gz' to get the '.json' path

    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(json_path, 'wb') as f_out:
                f_out.write(f_in.read())
        logging.info(f"Extracted {gz_path} to {json_path}")

        if process_json_file(json_path):
            os.remove(gz_path)
            os.remove(json_path)
            logging.info(f"Deleted {gz_path} and {json_path}")
        else:
            os.rename(gz_path, os.path.join(missed_folder, file_name))
            os.rename(json_path, os.path.join(missed_folder, json_path.split('/')[-1]))
            logging.info(f"Moved {gz_path} and {json_path} to {missed_folder}")

    except Exception as e:
                logging.error(f"Failed to process {file_name}: {str(e)}")
                if os.path.exists(gz_path):
                    os.rename(gz_path, os.path.join(missed_folder, file_name))
                if os.path.exists(json_path):
                    os.rename(json_path, os.path.join(missed_folder, json_path.split('/')[-1]))
                logging.info(f"Moved {gz_path} and {json_path} to {missed_folder} due to error")

def get_last_downloaded():
    if os.path.exists(tracking_file):
        with open(tracking_file, 'r') as file:
            last_downloaded = file.read().strip()
        if last_downloaded:
            return datetime.strptime(last_downloaded, '%Y-%m-%d-%H')
    return None

def update_last_downloaded(dt):
    with open(tracking_file, 'w') as file:
        file.write(dt.strftime('%Y-%m-%d-%H'))

def do_harvest_and_inject():
    with open('config.json', 'r') as file:
        config = json.load(file)    

    start_date = datetime.strptime(config['start_date'], '%Y-%m-%d')
    end_date = datetime.strptime(config['end_date'], '%Y-%m-%d')
    delta = timedelta(days=1)

    os.makedirs(download_folder, exist_ok=True)
    if not os.path.exists(tracking_file):
        with open(tracking_file, 'w') as file:
            file.write('')

    last_downloaded_dt = get_last_downloaded()
    if last_downloaded_dt:
        start_date = last_downloaded_dt + timedelta(hours=1) 

    current_date = start_date
    while current_date <= end_date:
        for hour in range(24):
            file_name = f"{current_date.strftime('%Y-%m-%d')}-{hour}.json.gz"
            file_path = os.path.join(download_folder, file_name)
            url = f"https://data.gharchive.org/{file_name}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    update_last_downloaded(current_date.replace(hour=hour))
                    logging.info(f"Successfully downloaded {file_name}")
                    extract_and_process_file(file_path)
                else:
                    logging.warning(f"Failed to download {file_name}, status code {response.status_code}")
            except Exception as e:
                logging.error(f"Error downloading {file_name}: {str(e)}")
        current_date += delta
     

if __name__ == "__main__":
    logging.info("Starting the injector service...")
    do_harvest_and_inject()
    logging.info("Injector service exitting...")