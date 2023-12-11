#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/12 14:53:20
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import logging
import os


logger = logging.getLogger(__name__)


def getlog(env, name):
    exist = name in logging.Logger.manager.loggerDict
    rs_logger = logging.getLogger(name)
    if not exist:
        logger.info(f"create logger with {env=}, {name=}")
        if env in ["dev", "local"]:
            rs_logger.propagate = False
            rs_logger.setLevel(logging.DEBUG)
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(fmt=logging.Formatter(
                "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S'))
            rs_logger.addHandler(streamHandler)
        else:
            rs_logger.propagate = False
            rs_logger.setLevel(logging.INFO)
            streamHandler = logging.StreamHandler()
            streamHandler.setFormatter(fmt=logging.Formatter(
                "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d-%H:%M:%S'))
            rs_logger.addHandler(streamHandler)

    return rs_logger


_FMT_MAP = {
    "simple": logging.Formatter(
        "%(asctime)s [%(levelname)s]%(message)s", datefmt='%Y-%m-%d-%H:%M:%S'),
    "detail":   logging.Formatter(
        "%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s", datefmt='%Y-%m-%d %H:%M:%S')

}


def getlog_detail(name, level, format_type: str = "simple", do_print=True, do_file=False, propagate=False,
                  log_dir: str = None, file_type="time_rotate", file_config=dict(when='d', interval=1, backupCount=7)):
    exist = name in logging.Logger.manager.loggerDict
    rs_logger = logging.getLogger(name)
    if exist:
        return rs_logger
    fmt = _FMT_MAP[format_type]

    rs_logger.propagate = propagate
    rs_logger.setLevel(level)

    if do_print:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(fmt=fmt)
        rs_logger.addHandler(streamHandler)
    if do_file:
        log_dir = log_dir or os.environ.get("LOG_DIR", "/tmp/logs")
        file_path = os.path.join(log_dir, name + ".log")
        if file_type == "time_rotate":
            filehandler = logging.handlers.TimedRotatingFileHandler(file_path, **file_config)
            filehandler.suffix = "%Y-%m-%d_%H-%M-%S.log"  # 设置历史文件 后缀
            filehandler.setFormatter(fmt)
            rs_logger.addHandler(filehandler)
    return rs_logger
