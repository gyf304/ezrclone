import sys
import os
import argparse
from common import *

ARGS = [
    (('file', ), {'type': str, 'nargs': '*'}),
    (('-a', '--all'), {'action': 'store_true'})
]

def add(options=tuple(), out_file=sys.stdout, err_file=sys.stderr, verbose=0, **kwargs):
    try:
        root_dir = find_root_dir()
        config = load_config()
        state = load_state()
    except RootNotFoundError:
        print(ROOT_NOT_FOUND_ERROR_STR, file=err_file)
        sys.exit(1)
    except InvalidConfigError:
        print(CONFIG_ERROR_STR, file=err_file)
        sys.exit(1)
    except InvalidStateError:
        print(STATE_ERROR_STR, file=err_file)
        sys.exit(1)
    parser = argparse.ArgumentParser()
    for (args, kwargs) in ARGS:
        parser.add_argument(*args, **kwargs)
    args = parser.parse_args(options)
    if args.all:
        state['include'] = 'all'
    elif 'include' not in state:
        state['include'] = []
    if state['include'] != 'all':
        for file_name in args.file:
            file_path = os.sep + os.path.relpath(file_name, root_dir)
            file_type = 'file'
            if os.path.isdir(file_name) or file_name.endswith(os.sep):
                file_type = 'dir'
            file_entry = (file_path, file_type)
            if file_entry not in map(tuple, state['include']):
                state['include'].append(file_entry)
                if verbose > 0:
                    print('{} added'.format(file_name), file=err_file)
            else:
                if verbose > 0:
                    print('{} skipped'.format(file_name), file=err_file)
    save_state(state)
