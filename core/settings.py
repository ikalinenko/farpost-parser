import logging
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


logging.basicConfig(
    level=logging.DEBUG,
    filename=os.path.join(BASE_DIR, 'root.log')
)
