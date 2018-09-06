import os

import utils


FLASK_DEBUG = os.getenv('DEBUG') == 'true'

FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = os.getenv('FLASK_PORT', 5001)

MONGO_HOST = os.getenv('MONGO_HOST', 'db')
MONGO_PORT = os.getenv('MONGO_PORT', 27017)
MONGO_DEFAULT_DB = os.getenv('MONGO_DEFAULT_DB', 'db')

TILE_OUTPUT_DIR = os.getenv('TILE_OUTPUT_DIR', utils.get_data_path('tiles/output'))
