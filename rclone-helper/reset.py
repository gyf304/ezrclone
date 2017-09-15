from common import *
import sys
import os

def reset(options=tuple(), out_file=sys.stdout, err_file=sys.stderr, **kwargs):
    try:
        config_dir = find_config_dir()
        config = load_config()
    except RootNotFoundError:
        print('Unable to load config', file=err_file)
        return 1
    try:
        os.remove(os.path.join(config_dir, STATE_FILE_NAME))
    except FileNotFoundError:
        pass
    try:
        os.remove(os.path.join(config_dir, FILTER_LIST_FILE_NAME))
    except FileNotFoundError:
        pass
