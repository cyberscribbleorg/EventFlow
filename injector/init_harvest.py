import logging
import time
from tasks.do_harvest import do_harvest

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

if __name__ == "__main__":
    logging.info("Starting the initial harvest...")
    result = do_harvest.delay()
    time.sleep(2)
    logging.info("Initial harvest task has been enqueued.")