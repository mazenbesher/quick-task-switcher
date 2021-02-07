import os

from globals import config, JSONConfig


def load_json_config():
    if os.path.exists(config.json_config.config_path):
        with open(config.json_config.config_path) as fp:
            json_config = JSONConfig.from_json(fp.read())
        config.json_config = json_config


def save_json_config():
    json_config = config.json_config.to_json(indent=4)
    with open(config.json_config.config_path, 'w') as fp:
        fp.write(json_config)
