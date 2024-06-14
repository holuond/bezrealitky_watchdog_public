import logging
from dotenv import load_dotenv
from bezrealitky_watchdog import logging_, watchdog

load_dotenv()

logging_.configure_logging()
logger = logging.getLogger('bezrealitky_watchdog')

if __name__ == '__main__':
    logger.info('Started Bezrealitky Watchdog. Woof! 🐶')
    watchdog.run()
