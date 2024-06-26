from celery_app import app
from upload2pg import insert_event_if_not_exist, connect_with_retry, insert_events_bulk
import logging
from upload2pg import disconnect
import json
from utils import load_config
import logging


@app.task(bind=True)
def do_inject(self, file_path):
    config = load_config()
    conn = None
    batch_size = 5000  # Define the batch size
    try:
        conn = connect_with_retry(config)
        processed_count = 0

        with open(file_path, 'r') as file:
            batch = []
            for line in file:
                if line.strip():
                    try:
                        event = json.loads(line.strip())
                        batch.append(event)
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decoding error in file {file_path} on line {line}: {e}")
                        continue

                if len(batch) >= batch_size:
                    processed_count += process_batch(conn, batch, config)
                    batch = []

            # Process the remaining lines in the last batch
            if batch:
                processed_count += process_batch(conn, batch, config)

        logging.info(f"Processed count {processed_count}")
        disconnect(conn)
        return True
                
    except IOError as e:
        logging.error(f"IO error while reading file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing file {file_path}: {e}")
    finally:
        if conn:
            disconnect(conn)  # Ensure connection is closed in case of exceptions
            logging.info("Database connection closed.")

    return False

def process_batch(conn, batch, config):
    mode = config.get('mode', '@')
    if mode == '@':
        filtered_events = [event for event in batch if filter_event(event, config)]
        insert_events_bulk(conn, filtered_events)
        return len(filtered_events)
    else:
        insert_events_bulk(conn, batch)
        return len(batch)
    
def filter_event(event, config):
    users = config.get('users', [])
    projects = config.get('projects', [])

    actor = event['actor']['login']
    repo_name = event['repo']['name']

    if users and actor in users:
        return True
    if projects and repo_name in projects:
        return True
    
    return False
