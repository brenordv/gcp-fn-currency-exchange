# -*- coding: utf-8 -*-
"""utils.py
Utilitarian methods and functions to help out a little.

"""

import json
from pathlib import Path
from timeit import default_timer as timer
from datetime import timedelta, datetime
from typing import Union, List
from os import environ

__REQUIRED_KEYS__ = [
    "alpha_vantage_key",
    "mongo_user",
    "mongo_pass",
    "mongo_database",
    "threshold",
    "telegram_bot_key",
    "from_currency",
    "to_currency"
]


def validate_runtime_vars(secrets: dict) -> (bool, List[str]):
    if secrets is None:
        return False

    invalid_keys = [k for k in __REQUIRED_KEYS__ if secrets.get(k) is None]

    return len(invalid_keys) == 0, invalid_keys


def get_runtime_variables():
    secrets_file = Path("./secrets.json")

    if secrets_file.exists():
        with open(secrets_file, "r", encoding="utf-8") as file:
            secrets = json.load(file)
    else:
        secrets = {
            "alpha_vantage_key": environ.get("alpha_vantage_key"),
            "mongo_user": environ.get("mongo_user"),
            "mongo_pass": environ.get("mongo_pass"),
            "mongo_database": environ.get("mongo_database"),
            "telegram_bot_key": environ.get("telegram_bot_key"),
            "telegram_chat_id": environ.get("telegram_chat_id"),
            "threshold": float(environ.get("threshold", 0.05)),
            "from_currency": environ.get("from_currency", "CAD"),
            "to_currency": environ.get("to_currency", "BRL")
        }

    is_valid, invalid_keys = validate_runtime_vars(secrets)
    if not is_valid:
        raise ValueError(f"Could not load the following variables: {', '.join(invalid_keys)}")

    return secrets


class StopWatch(object):
    """ StopWatch

    A class that manages a StopWatch, so you can easily measure elapsed time of operations.

    Attributes
    ----------
    start_datetime : datetime
        Date and time when the time started.

    end_datetime : datetime
        Date and time when the time stopped.


    Methods
    -------
    start() -> None:
        Starts the timer.

    elapsed(raw: bool = False) -> Union[str, timedelta, None]:
        Returns the current elapsed time.

    end(raw: bool = False) -> Union[str, timedelta, None]:
        Stops the timer and returns the total elapsed time.

    """

    def __init__(self, auto_start: bool = False):
        """
        Creates a new instance of this Stopwatch.

        :param auto_start: if true, will auto start the timer.
        """
        self.__start_timer__ = None
        self.__end_timer__ = None
        self.start_datetime = None
        self.end_datetime = None

        if auto_start:
            self.start()

    def start(self) -> None:
        """
        Starts the timer.
        :return: None
        """
        self.start_datetime = datetime.now()
        self.__start_timer__ = timer()

    def elapsed(self, raw: bool = False) -> Union[str, timedelta, None]:
        """
        Returns the elapsed time either from a current running timer or the total timer,
        if it has been stopped.

        :param raw: if true, will return a timedelta object with the elapsed time.
                    otherwise, will return the string version (days.hours:minutes:seconds.ms)

        :return: elapsed time either in a string or timedelta format.
                 if this method is called before starting the timer, will return None.
        """
        if self.__start_timer__ is None:
            return None

        end = timer() if self.__end_timer__ is None else self.__end_timer__
        elapsed_time = timedelta(seconds=end - self.__start_timer__)

        if raw:
            return elapsed_time
        return str(elapsed_time)

    def end(self, raw: bool = False) -> Union[str, timedelta, None]:
        """
        Stops the current timer.
        If it's called multiple times, after the first call, this method will just
        return the elapsed time. (Same behaviour has elasped() method)

        :param raw: if true, will return a timedelta object with the elapsed time.
                    otherwise, will return the string version (days.hours:minutes:seconds.ms)

        :return: elapsed time either in a string or timedelta format.
        """
        if self.__end_timer__ is not None:
            return self.elapsed(raw=raw)

        self.end_datetime = datetime.now()
        self.__end_timer__ = timer()

        return self.elapsed(raw=raw)
