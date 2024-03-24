import json
import os
from types import SimpleNamespace


def get_user_config():
    if os.path.exists('.config'):
        with open('.config', 'r') as f:
            return SimpleNamespace(**json.load(f))

    config = SimpleNamespace()
    config.username = input('please enter username:')
    write_config(config)
    return config


def write_config(config):
    with open('.config', 'w') as f:
        json.dump(vars(config), f)

