from celery_app import app
import logging
import gzip
import os
from utils import load_config, get_download_folder, get_errror_folder

from tasks.do_inject import do_inject

DOWNLOAD_FOLDER = get_download_folder()
MISSED_FOLDER = get_errror_folder()

@app.task(bind=True)
def do_extract(self, file_name):
    config = load_config()
    gz_path = os.path.join(DOWNLOAD_FOLDER, file_name)
    json_path = gz_path[:-3]  # Remove '.gz' to get the '.json' path

    try:
        with gzip.open(gz_path, 'rb') as f_in:
            with open(json_path, 'wb') as f_out:
                f_out.write(f_in.read())
        logging.info(f"Extracted {gz_path} to {json_path}")

        if do_inject(json_path):
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