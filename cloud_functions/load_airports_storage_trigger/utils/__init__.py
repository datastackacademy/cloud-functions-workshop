
import logging
import sys

import yaml
from flask import Request

# setup logging and logger
logging.basicConfig(format='[%(levelname)-5s][%(asctime)s][%(module)s:%(lineno)04d] : %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)
logger: logging.Logger = logging


def load_config(path_to_yaml: str) -> dict:
    with open(path_to_yaml, 'r', encoding='utf-8') as yaml_file:
        return yaml.full_load(yaml_file)


config = load_config("./config.yml")
