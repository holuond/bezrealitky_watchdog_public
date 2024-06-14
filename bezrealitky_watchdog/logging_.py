import logging
import logging.config
from pathlib import Path
from typing import Callable

import yaml
from termcolor import colored

from bezrealitky_watchdog.constants import ROOT_PROJECT_DIR


def configure_logging():
    logging.captureWarnings(True)
    configure_logging_using_file_config(ROOT_PROJECT_DIR / 'logging.yaml')


def configure_logging_using_file_config(config_path: Path,
                                        parse_file_to_dict: Callable = yaml.safe_load) -> None:
    try:
        with open(config_path, 'r') as file:
            logging.config.dictConfig(parse_file_to_dict(file))
    except FileNotFoundError:
        logging.error(f"Logging configuration file not found, {config_path=}.")
    except yaml.YAMLError as e:
        logging.error(f"Error in parsing logging configuration file {config_path}: {e}")


class ColoredFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt):
        super().__init__(fmt, datefmt=datefmt)
        self.LEVEL_COLORS = {logging.DEBUG: 'light_grey', logging.WARNING: 'yellow', logging.ERROR: 'red', logging.CRITICAL: 'red'}

    def format(self, record):
        message = super().format(record)
        color = self.LEVEL_COLORS.get(record.levelno, None)
        message = colored(message, color)
        return message
