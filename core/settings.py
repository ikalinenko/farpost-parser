import logging
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname) %(asctime) - %(message)',
    filename=os.path.join(BASE_DIR, 'root.log')
)
