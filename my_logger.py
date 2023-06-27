import datetime
import logging
from os import path, mkdir, environ

from colorlog import ColoredFormatter
from dotenv import load_dotenv

load_dotenv(verbose=True)


class LogLevelFilter(logging.Filter):
    """https://stackoverflow.com/a/7447596/190597 (robert)"""

    def __init__(self, level):
        super().__init__()
        self.level = level

    def filter(self, record):
        # Just revert >= to <= then get only current level or lower.
        return record.levelno <= self.level


class MyLogger:
    _logger = None
    log_level = environ.get("LOG_LEVEL", "INFO").upper()

    def __new__(cls, *args, **kwargs):
        if cls._logger is None:
            cls._logger = super().__new__(cls, *args, **kwargs)
            cls._logger = logging.getLogger("peewee")
            cls._logger.setLevel(cls.log_level)

            file_fmt = logging.Formatter(
                fmt="%(asctime)s %(levelname)s %(thread)s [%(filename)s:%(lineno)s %(funcName)s] :: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            console_fmt = ColoredFormatter(
                fmt="%(asctime)s %(log_color)s%(levelname)-8s%(reset)s| [%(filename)s:%(lineno)s %(funcName)s]"
                    "%(reset)s | %(log_color)s%(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                reset=True,
                log_colors={
                    "DEBUG": "bold_cyan",
                    "INFO": "bold_green",
                    "WARNING": "bold_yellow",
                    "ERROR": "bold_red",
                    "CRITICAL": "bold_red,bg_white",
                },
                secondary_log_colors={},
                style="%",
            )

            now = datetime.datetime.now()
            dirname = "./logs"

            if not path.isdir(dirname):
                mkdir(dirname)

            ona_log = dirname + "/ona_" + now.strftime("%Y-%m-%d") + ".log"

            ona_log_file = path.join(path.dirname(path.abspath(__file__)), ona_log)
            ona_file_handler = logging.FileHandler(ona_log_file)

            # ona_file_handler.setLevel(logging.WARN)

            stream_handler = logging.StreamHandler()

            ona_file_handler.setFormatter(file_fmt)
            stream_handler.setFormatter(console_fmt)

            cls._logger.addHandler(stream_handler)
            cls._logger.addHandler(ona_file_handler)

        return cls._logger
