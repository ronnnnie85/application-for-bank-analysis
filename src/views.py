import logging
import os

from src import loggers

name = os.path.splitext(os.path.basename(__file__))[0]
file_name = f"{name}.log"
logger = loggers.create_logger(name, file_name, logging.DEBUG)


def get_data_main(date_time: str) -> str:
    """Принимает на вход дату и время и возвращает json с данными"""
    pass


def get_data_events(date_time: str, date_period: str = "M") -> str:
    """Принимает строку с датой и необязательный параметр диапазон.
    Возвращает json с данными"""
    pass
