#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/12 14:53:20
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''
import logging


logger = logging.getLogger(__name__)


def getlog(env, name):
    exist = name in logging.Logger.manager.loggerDict
    rs_logger = logging.getLogger(name)
    if not exist:
        logger.info(f"create logger with {env=}, {name=}, {exist=}")
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