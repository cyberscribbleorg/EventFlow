from celery_app import app
from upload2pg import insert_event_if_not_exist, connect_with_retry, insert_events_bulk
import logging
import json
from utils import load_config

@app.task(bind=True)
def do_inject(self, file_path):
    config = load_config()
    conn = connect_with_retry(config)
    processed_count = 0
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            if not lines:
                logging.warning(f"Empty file..skipping..: {file_path}")
                return False

            events = [json.loads(line.strip()) for line in lines]
            mode = config.get('mode', '@')
            if mode == '@':
                filtered_events = []
                for event in events:
                    if filter_event(event, config):
                        filtered_events.append(event)
                        processed_count += 1
                insert_events_bulk(conn, filtered_events)
                logging.info(f"Processed count {processed_count}")
                return True
            else:
                insert_events_bulk(conn, events)
                processed_count = len(events)
                logging.info(f"Processed count {processed_count}")
                return True
                
    except json.JSONDecodeError as e:
        logging.error(f"JSON decoding error in file {file_path}: {e}")
    except IOError as e:
        logging.error(f"IO error while reading file {file_path}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error processing file {file_path}: {e}")
    finally:
        conn.close()
        logging.info("Database connection closed.")
    return False

def filter_event(event, config):
    mode = config.get('mode', '@')
    if mode == '@':
        users = config.get('users', [])
        projects = config.get('projects', [])

        actor = event['actor']['login']
        repo_name = event['repo']['name']

        if users and actor in users:
            return True
        if projects and repo_name in projects:
            return True
        return False
    else:
        return True 