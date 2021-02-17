import datetime
import os
from pathlib import Path

from globals import config, JSONConfig


def validate_config():
    assert len(config.json_config.desktop_names) == config.json_config.desktops_number
    assert len(config.json_config.desktop_names_history) <= config.json_config.desktop_names_history_max_size
    assert 0.0 < config.json_config.main_window_opacity <= 1.0
    assert config.json_config.grab_area_min_size[0] > 0
    assert config.json_config.grab_area_min_size[1] > 0
    assert len(config.json_config.config_path) != 0
    assert config.json_config.desk_name_char_limit > 0
    assert config.json_config.check_interval > 10

    for desk_name in config.json_config.desktop_names + config.json_config.desktop_names_history:
        assert 1 <= len(desk_name) <= config.json_config.desk_name_char_limit


def load_json_config():
    if os.path.exists(Path(config.json_config.config_path)):
        with open(Path(config.json_config.config_path)) as fp:
            json_config = JSONConfig.from_json(fp.read())
        config.json_config = json_config
    validate_config()


def save_json_config():
    # save quit time
    config.json_config.quit_time = datetime.datetime.now().timestamp()

    # save session durations
    config.json_config.prev_durations = {}
    for desk_id in range(config.desk_count):
        name = config.json_config.desktop_names[desk_id]
        dur = config.timers[desk_id].get_elapsed()
        config.json_config.prev_durations[name] = dur

    json_config = config.json_config.to_json(indent=2)
    with open(config.json_config.config_path, 'w') as fp:
        fp.write(json_config)
