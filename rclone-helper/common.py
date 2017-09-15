import os
import json


class RootNotFoundError(Exception):
    pass


class InvalidConfigError(Exception):
    pass


class InvalidStateError(Exception):
    pass


HELPER_DIRECTORY_NAME = '.rclone-helper'
CONFIG_FILE_NAME = 'config.json'
STATE_FILE_NAME = 'state.json'
FILTER_LIST_FILE_NAME = 'filter_list'

ROOT_NOT_FOUND_ERROR_STR = r'fatal: Not a repository (or any of the parent directories): ' \
    + HELPER_DIRECTORY_NAME + r' (Did you init?)'
CONFIG_ERROR_STR = r'fatal: Config cannot be loaded.'
STATE_ERROR_STR = r'fatal: State is invalid. Try reset.'


def find_root_dir():
    current_dir = os.getcwd()
    root_dir = current_dir
    while not os.path.isdir(os.path.join(root_dir, HELPER_DIRECTORY_NAME)):
        new_dir = os.path.dirname(root_dir)
        if root_dir == new_dir:
            raise RootNotFoundError
        root_dir = new_dir
    return root_dir


def find_config_dir():
    root_dir = find_root_dir()
    return os.path.join(root_dir, HELPER_DIRECTORY_NAME)


def load_config():
    """Loads config to a dict"""
    config_dir = find_config_dir()
    config_path = os.path.join(find_config_dir(), CONFIG_FILE_NAME)
    with open(config_path, encoding='utf-8') as file:
        try:
            config = json.load(file)
        except json.JSONDecodeError:
            raise InvalidConfigError
    if 'remote' not in config or not isinstance(config['remote'], dict):
        raise InvalidConfigError
    if 'exclude' not in config or not isinstance(config['exclude'], list):
        raise InvalidConfigError
    if 'bin' not in config or not isinstance(config['bin'], str):
        raise InvalidConfigError
    return config


def load_state():
    try:
        config_dir = find_config_dir()
        state_path = os.path.join(find_config_dir(), STATE_FILE_NAME)
        with open(state_path, encoding='utf-8') as file:
            state = json.load(file)
    except FileNotFoundError:
        return dict()
    except json.JSONDecodeError:
        raise InvalidStateError
    return state


def save_state(state):
    config_dir = find_config_dir()
    state_path = os.path.join(find_config_dir(), STATE_FILE_NAME)
    with open(state_path, 'w', encoding='utf-8') as file:
        json.dump(state, file)
