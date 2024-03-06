#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/12 14:53:20
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
from enum import Enum
import logging
import os
from logging.handlers import TimedRotatingFileHandler



logger = logging.getLogger(__name__)


def getlog(env:str, name:str):
    exist = name in logging.Logger.manager.loggerDict
    rs_logger = logging.getLogger(name)
    if not exist:
        logger.info(f"create logger with {env=}, {name=}")
        if env.lower() in ["dev", "local"]:
            rs_logger.propagate = False
            rs_logger.setLevel(logging.DEBUG)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(fmt=logging.Formatter(
                "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
            rs_logger.addHandler(stream_handler)
        else:
            rs_logger.propagate = False
            rs_logger.setLevel(logging.INFO)
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(fmt=logging.Formatter(
                "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d-%H:%M:%S'))
            rs_logger.addHandler(stream_handler)

    return rs_logger

get_log = getlog


_FMT_MAP = {
    "raw": logging.Formatter("%(message)s"),
    "simple": logging.Formatter(
        "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d-%H:%M:%S'),
    "detail":   logging.Formatter(
        "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S')
}


class LoggingFormat(Enum):
    RAW = logging.Formatter("%(message)s")
    SIMPLE = logging.Formatter(
        "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d-%H:%M:%S')
    DETAIL=logging.Formatter(
        "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S')


class LoguruFormat(str, Enum):
    RAW = "{message}"
    SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level>|  - <level>{message}</level>"
    DETAIL="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <level>{level: <8}</level> | <cyan>{file}</cyan>:<cyan>{line}</cyan>[<cyan>{function}</cyan>] - <level>{message}</level>"
    FILE_DETAIL="{time:YYYY-MM-DD HH:mm:ss.SSS} [{level: <8}] | {name}:{line}[{function}] - {message}"
    

def getlog_detail(name, level, format_type: str = "simple",
                  do_print=True, print_format_type=None, print_level=None,
                  do_file=False, file_format_type=None,  file_level = None, file_type="time_rotate", file_config=dict(when='d', interval=1, backupCount=7),
                  propagate=False, log_dir: str = None,):
    exist = name in logging.Logger.manager.loggerDict
    rs_logger = logging.getLogger(name)
    if exist:
        return rs_logger
    
    rs_logger.propagate = propagate
    rs_logger.setLevel(level)

    if do_print:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(fmt=_FMT_MAP[print_format_type if print_format_type else format_type])
        streamHandler.setLevel(print_level if print_level else level)
        rs_logger.addHandler(streamHandler)
        
    if do_file:
        log_dir = log_dir or os.environ.get("LOG_DIR", "/tmp/logs")
        file_path = os.path.join(log_dir, name + ".log")
        os.makedirs(log_dir, exist_ok=True)
        if file_type == "time_rotate":
            filehandler = TimedRotatingFileHandler(file_path, **file_config)
            filehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"  # 设置历史文件 后缀
            filehandler.setFormatter(_FMT_MAP[file_format_type if file_format_type else format_type])
            filehandler.setLevel(file_level if file_level else level)
            rs_logger.addHandler(filehandler)
    return rs_logger


def get_file_log(name, log_dir):
    return getlog_detail(name=name, format_type="simple", level=logging.DEBUG,
                         do_print=True, print_format_type="raw", print_level=logging.INFO,
                         do_file=True, file_format_type="detail", file_level=logging.DEBUG, log_dir=log_dir)




