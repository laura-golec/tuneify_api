import toml
import json
import re

from keys import *


with open(RIP_SETTINGS_RULES) as json_file:
    rules = json.load(json_file)

# ===============================================================================================

# validation section
def validate_string(value):
    return isinstance(value, str)

def validate_bool(value):
    return isinstance(value, bool)

def validate_range(value, rule):
    if value.isdigit():
        value = int(value)
    if not isinstance(value, int):
        return False
    if ':' in rule:
        min, max = list(map(int,rule[6:].split(':')))
        return  min <= value and value <=max
    elif ',' in rule:
        min, max = list(map(int,rule[6:].split(',')))
        return value == min or value == max
    else:
        max = int(rule[6:])
        return value == max

def validate_forbidden(value):
    return False

def validate_codec(value):
    return value in ['FLAC', 'ALAC', 'OPUS', 'MP3', 'VORBIS', 'AAC']

def validate_size(value):
    return value in ['thumbnail', 'small', 'large', 'original']

def validate_string_list(value):
    if isinstance(value, list):
        return all(isinstance(item, str) for item in value)
    return False

def validate_folder(value):
    available_keys = ['albumartist', 'title', 'year', 'bit_depth', 'sampling_rate', 'id', 'albumcomposer']
    keys = re.findall(r'{(.*?)}', value)
    for key in keys:
        if key not in available_keys:
            return False
    return True

def validate_track(value):
    available_keys = ['tracknumber', 'artist', 'albumartist', 'composer', 'title', 'albumcomposer', 'explicit']
    keys = re.findall(r'{(.*?)}', value)
    for key in keys:
        if key not in available_keys:
            return False
    return True

def validate_sources(value):
    return value in ['qobuz', 'tidal', 'deezer', 'soundcloud', 'youtube']

validation_dict= {
    'string': validate_string,
    'bool': validate_bool,
    'forbidden': validate_forbidden,
    'codec': validate_codec,
    'size': validate_size,
    'string_list': validate_string_list,
    'folder': validate_folder,
    'track': validate_track,
    'sources': validate_sources
}

# ==============================================================================================================

# rule change section
def load_toml_config(file_path):
    with open(file_path, 'r') as file:
        config = toml.load(file)
    return config

def save_toml_config(config, file_path):
    with open(file_path, 'w') as file:
        toml.dump(config, file)

def update_config_value(config, path, value):
    nested_config = config
    for key in path[:-1]:
        nested_config = nested_config[key]
    nested_config[path[-1]] = str(value)

def validate_change(value, rule):
    if 'range' in rule:
        return validate_range(value, rule)
    elif rule in validation_dict:
        return validation_dict[rule](value)
    else:
        print('failing ', value, rule)
        return False

def change_settings(file_path, path, value):
    # Load the config
    config = load_toml_config(file_path)
    nested_config = rules

    for key in path[:-1]:
        nested_config = nested_config[key]
    rule = nested_config[path[-1]]

    if validate_change(value, rule):
        update_config_value(config, path, value)
        save_toml_config(config, file_path)
        return {'Success': 'changed rule!'}
    return {'Error': f'{rule in validation_dict}'}