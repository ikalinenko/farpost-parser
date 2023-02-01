import logging
import os
from pathlib import Path
from environs import Env


BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

RUCAPTCHA_API_KEY = env.str('RUCAPTCHA_API_KEY')
GOOGLE_SITE_KEY = env.str('GOOGLE_SITE_KEY')

SMTP_EMAIL_HOST = env.str('SMTP_EMAIL_HOST')
SMTP_EMAIL_PORT = env.int('SMTP_EMAIL_PORT')
SMTP_EMAIL_USER = env.str('SMTP_EMAIL_USER')
SMTP_EMAIL_PASSWORD = env.str('SMTP_EMAIL_PASSWORD')

EMAIL_RECIPIENTS = env.list('EMAIL_RECIPIENTS')


logging.basicConfig(
    level=logging.DEBUG,
    format='{levelname} {asctime} - {message}',
    style='{',
    filename=os.path.join(BASE_DIR, 'root.log')
)
