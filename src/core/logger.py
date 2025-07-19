import logging
import os
import sys
from logging import Logger

from colorlog import ColoredFormatter

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__)).split("core")[0]


class ProjectPathFormatter(ColoredFormatter):
    def format(self, record):
        record.project_path = os.path.relpath(record.pathname, PROJECT_ROOT)
        return super().format(record)


def setup_logger(name: str = "bot", level: int = logging.INFO) -> Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if logger.hasHandlers():
        return logger

    handler = logging.StreamHandler(sys.stdout)

    formatter = ProjectPathFormatter(
        fmt="%(log_color)s%(asctime)s | %(levelname)-7s | %(name)s | %(project_path)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


logger = setup_logger()
