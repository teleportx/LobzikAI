import gzip
import logging
import os
import platform
import sys
from pathlib import Path

from loguru import logger

import config

project_name: str


class InterceptHandler(logging.Handler):
    LEVELS_MAP = {
        logging.CRITICAL: "CRITICAL",
        logging.ERROR: "ERROR",
        logging.WARNING: "WARNING",
        logging.INFO: "INFO",
        logging.DEBUG: "DEBUG",
    }

    def _get_level(self, record):
        return self.LEVELS_MAP.get(record.levelno, record.levelno)

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        logger.opt(exception=record.exc_info).log(level, record.getMessage())


def __init__(__project_name: str):
    global project_name

    project_name = __project_name

    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    logger.remove()

    logger_level = 'INFO'
    if config.debug:
        logger_level = 'DEBUG'

    logger.add(sys.stderr, level=logger_level)

    logger.info(f'LobzikAI | {project_name}')
    if config.debug:
        logger.warning('APP IN DEBUG MODE')

    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Running on: {platform.system()} {platform.release()} ({os.name})")
