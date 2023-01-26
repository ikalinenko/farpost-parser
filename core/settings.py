import logging
import os
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR)

RUCAPTCHA_API_KEY = os.environ.get('RUCAPTCHA_API_KEY')
GOOGLE_SITE_KEY = os.environ.get('GOOGLE_SITE_KEY')


logging.basicConfig(
    level=logging.DEBUG,
    format='{levelname} {asctime} - {message}',
    style='{',
    filename=os.path.join(BASE_DIR, 'root.log')
)
