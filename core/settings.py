import logging
import os
from pathlib import Path
from environs import Env


BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

RUCAPTCHA_API_KEY = env.str('RUCAPTCHA_API_KEY')
GOOGLE_SITE_KEY = env.str('GOOGLE_SITE_KEY')


logging.basicConfig(
    level=logging.DEBUG,
    format='{levelname} {asctime} - {message}',
    style='{',
    filename=os.path.join(BASE_DIR, 'root.log')
)
