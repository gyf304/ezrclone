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


def gen_filter(exclude, include, file):
    for item in exclude:
        file.write('- ' + item + '\n')
    for item in include:
        file.write('+ ' + item + '\n')


def pushpull(options=tuple(), out_file=sys.stdout, err_file=sys.stderr, mode='push', verbose=0, yes=None):
    # load config
    try:
        root_dir = find_root_dir()
        config_dir = find_config_dir()
        config = load_config()
        state = load_state()
    except RootNotFoundError:
        print(ROOT_NOT_FOUND_ERROR_STR, file=err_file)
        return 1
    except InvalidConfigError:
        print(CONFIG_ERROR_STR, file=err_file)
        return 1
    except InvalidStateError:
        print(STATE_ERROR_STR, file=err_file)
        return 1
    # load args
    parser = argparse.ArgumentParser()
    for (args, kwargs) in ARGS:
        parser.add_argument(*args, **kwargs)
    parser.add_argument('options', nargs=argparse.REMAINDER)
    args = parser.parse_args(options)
    remote_name = args.remote
    if remote_name not in config['remote']:
        print(REMOTE_NOT_FOUND_ERROR_STR.format(remote_name))
        return 1
    bin = config['bin']
    remote = config['remote'][remote_name]
    filter_file_path = os.path.join(config_dir, FILTER_LIST_FILE_NAME)
    rclone_args = [bin, 'sync']
    rclone_args += remote.get('flags', [])
    rclone_args += args.options
    rclone_args += ['--filter-from', filter_file_path]
    if 'include' not in state or \
        (isinstance(state['include'], list) and len(state['include']) == 0):
        print(NO_FILE_STR, file=err_file)
        return 1
    with open(filter_file_path, 'w') as filter_file:
        # open file
        for exclude_item in config['exclude']:
            filter_file.write('- ' + exclude_item + '\n')
            # do not include config folder
        filter_file.write('- /' + HELPER_DIRECTORY_NAME + '/\n')
        file_list = state['include']
        if isinstance(state['include'], list):
            for (file_path, file_type) in file_list:
                if file_type == 'dir':
                    dir_path = file_path if file_path.endswith(
                        os.sep) else file_path + os.sep
                    dir_path_escaped = escape(dir_path) + '**'
                    filter_file.write('+ ' + dir_path_escaped + '\n')
                escaped = escape(file_path)
                filter_file.write('+ ' + escaped + '\n')
        # all files included
        elif state['include'] == 'all':
            pass
        else:
            pass
    if mode == 'push':
        rclone_args += [root_dir, remote_name + ':' + remote['dir']]
    elif mode == 'pull':
        rclone_args += [remote_name + ':' + remote['dir'], root_dir]
    print(*rclone_args, file=err_file)
    if not yes:
        subprocess.call(rclone_args + ['--dry-run'], stdout=out_file, stderr=err_file)
    prompt_answer = 'yes' if yes else input('Is that OK? {yes,no} ')
    if prompt_answer == 'yes':
        subprocess.call(rclone_args, stdout=out_file, stderr=err_file)
        reset()
        return 0
    else:
        return 1


def push(*args, **kwargs):
    pushpull(*args, **kwargs, mode='push')


def pull(*args, **kwargs):
    pushpull(*args, **kwargs, mode='pull')
