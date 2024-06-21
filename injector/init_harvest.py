import logging
import time
from tasks.do_harvest import do_harvest
from utils import load_config
from upload2pg import connect_with_retry, disconnect , create_db, initialize_tables, insert_eventconfig

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def setup():
    config = load_config()
    conn = connect_with_retry(config)
    if conn:
        if create_db(config):
            initialize_tables(conn)
            insert_eventconfig(conn,config)
        disconnect(conn)
        

if __name__ == "__main__":
    logging.info("Starting the initial harvest...")
    setup()
    result = do_harvest.delay()
    time.sleep(2)
    logging.info("Initial harvest task has been enqueued.")