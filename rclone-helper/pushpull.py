import sys
import argparse
import subprocess
import re

from common import *
from reset import reset

ARGS = [
    (('remote', ), {'type': str})
]

REMOTE_NOT_FOUND_ERROR_STR = r'fatal: Remote {} does not exist.'
NO_FILE_STR = r'Nothing to do.'

ESCAPE_REGEX_STR = r'([\[\]\*\?\{\}\\])'
ESCAPE_REGEX = re.compile(ESCAPE_REGEX_STR)


def escape(path):
    return ESCAPE_REGEX.sub(r'\\\1', path)


def pushpull(options=tuple(), out_file=sys.stdout, err_file=sys.stderr, mode='push', verbose=0, yes=None):
    # load config
    try:
        root_dir = find_root_dir()
        config_dir = find_config_dir()
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
    # load args
    parser = argparse.ArgumentParser()
    for (args, kwargs) in ARGS:
        parser.add_argument(*args, **kwargs)
    parser.add_argument('options', nargs=argparse.REMAINDER)
    args = parser.parse_args(options)
    remote_name = args.remote
    if remote_name not in config['remote']:
        print(REMOTE_NOT_FOUND_ERROR_STR.format(remote_name))
        sys.exit(1)
    bin = config['bin']
    remote = config['remote'][remote_name]
    rclone_args = [bin, 'sync']
    rclone_args += remote.get('flags', [])
    rclone_args += args.options
    # state not initialized
    if 'include' not in state:
        print(NO_FILE_STR, file=err_file)
        sys.exit(1)
    # a list of files
    elif type(state['include']) is list:
        file_list = state['include']
        if len(file_list) == 0:
            print(NO_FILE_STR, file=err_file)
            reset(None)
            sys.exit(0)
        else:
            for (file_path, file_type) in file_list:
                if file_type == 'dir' and not file_path.endswith(os.sep):
                    dir_path = file_path + os.sep
                    dir_path_escaped = escape(dir_path) + '**'
                    rclone_args += ('--include', dir_path_escaped)
                escaped = escape(file_path)
                rclone_args += ('--include', escaped)
    # all files included
    elif state['include'] == 'all':
        for exclude_item in config['exclude']:
            rclone_args += ('--exclude', exclude_item)
        # do not include config folder
        rclone_args += ('--exclude', '/' + HELPER_DIRECTORY_NAME + '/')
    else:
        pass
    if mode == 'push':
        rclone_args += [root_dir, remote_name + ':' + remote['dir']]
    elif mode == 'pull':
        rclone_args += [remote_name + ':' + remote['dir'], root_dir]
    print(*rclone_args, file=err_file)
    if not yes:
        subprocess.call(rclone_args + ['--dry-run'])
    prompt_answer = 'yes' if yes else input('Is that OK? {yes,no} ')
    if prompt_answer == 'yes':
        subprocess.call(rclone_args)
    reset(None)


def push(*args, **kwargs):
    pushpull(*args, **kwargs, mode='push')


def pull(*args, **kwargs):
    pushpull(*args, **kwargs, mode='pull')
