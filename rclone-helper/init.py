from common import *
import json
import os
import sys

DUMMY_CONFIG = {
    'exclude': [
        'Icon*'
    ],
    'remote': {
        'example': {
            'flags': ['--ignore-size'],
            'dir': '/'
        }
    },
    'bin': 'rclone'
}


def init(options=tuple(), out_file=sys.stdout, err_file=sys.stderr, **kwargs):
    try:
        os.mkdir(HELPER_DIRECTORY_NAME)
    except FileExistsError:
        pass
    config_path = os.path.join(HELPER_DIRECTORY_NAME, CONFIG_FILE_NAME)
    if os.path.exists(config_path):
        print('Config exists. Cannot reinit.', err_file)
        sys.exit(1)
    with open(config_path, 'w', encoding='utf-8') as file:
        json.dump(DUMMY_CONFIG, file)
    print('Config created at {}'.format(config_path))
