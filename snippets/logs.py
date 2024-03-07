#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/12 14:53:20
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
from enum import Enum
import os
import sys


class LoguruFormat(str, Enum):
    RAW = "{message}"
    SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level>|  - <level>{message}</level>"
    DETAIL = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan>[<cyan>{name}</cyan>:<cyan>{function}</cyan>] - <level>{message}</level>"
    FILE_DETAIL = "{time:YYYY-MM-DD HH:mm:ss.SSS} [{level: <8}] | {name}:{line}[{function}] - {message}"


def set_logger(env: str, log_dir=None):
    """_summary_

    Args:
        env (str): environment: dev/test/prod
        log_dir (_type_, optional): target log dir. Defaults to None.

    Returns:
        _type_: loguru logger
    """
    from loguru import logger
    if 0 in logger._core.handlers:
        logger.remove(0)
    fmt = LoguruFormat.DETAIL if env == "dev" else LoguruFormat.SIMPLE
    level = "DEBUG" if env == "dev" else "INFO"
    logger.add(sys.stdout, colorize=True, format=fmt, level=level)

    if log_dir:
        os.mkdir(log_dir, exist_ok=True)
        detail_log_path = os.path.join(log_dir, "detail.log")
        logger.add(detail_log_path, rotation="00:00", retention="7 days", enqueue=True, backtrace=True, level="DEBUG")
        output_log_path = os.path.join(log_dir, "output.log")
        logger.add(output_log_path, rotation="00:00", retention="30 days", enqueue=True, backtrace=True, level="INFO")
    return logger
