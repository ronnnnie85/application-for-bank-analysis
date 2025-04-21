import logging
import os
from unittest.mock import patch

from src.loggers import FORMAT_DATE_LOG, FORMAT_LOG, create_logger


def test_create_logger():
    tmp_path = os.path.join(os.path.dirname(__file__), "test.log")

    logger = create_logger("test", tmp_path, logging.DEBUG)
    handler = logger.handlers[0]
    formatter = handler.formatter

    assert logger.name == "test"
    assert logger.level == logging.DEBUG

    assert handler.baseFilename == tmp_path
    assert handler.mode == "w"
    assert handler.encoding == "utf-8"

    assert formatter._fmt == FORMAT_LOG
    assert formatter.datefmt == FORMAT_DATE_LOG


@patch("os.makedirs")
@patch("os.path.exists")
def test_create_logger_without_path(mock_exists, mock_makedirs):
    mock_exists.return_value = False
    tmp_path = os.path.join(os.path.dirname(__file__), "test.log")

    create_logger("test", tmp_path, logging.DEBUG)
