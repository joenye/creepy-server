import os
import sys
import logging

from common import utils


FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
FLASK_DEBUG = os.getenv('FLASK_DEBUG') != 'false'

MONGO_HOST = os.getenv('MONGO_HOST', 'db')
MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
MONGO_DEFAULT_DB = os.getenv('MONGO_DEFAULT_DB', 'db')

TILE_OUTPUT_DIR = os.getenv('TILE_OUTPUT_DIR', utils.get_data_path('renderer/output'))


def configure_logger():
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)
