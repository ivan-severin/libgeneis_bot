import os
import logging


TELEGRAM_ACCESS_TOKEN = os.environ["TELEGRAM_ACCESS_TOKEN"]
BITLY_USER = os.environ["BITLY_USER"]
BITLY_API_KEY = os.environ["BITLY_API_KEY"]

# Enable logging
logging.basicConfig(format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
                    level=logging.INFO)

