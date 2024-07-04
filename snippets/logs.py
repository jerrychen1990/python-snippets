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
from loguru import logger


class LoguruFormat(str, Enum):
    RAW = "{message}"
    SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: <8}</level>] - <level>{message}</level>"
    DETAIL = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [<level>{level: <8}</level>] - <cyan>{file}</cyan>:<cyan>{line}</cyan>[<cyan>{name}</cyan>:<cyan>{function}</cyan>] - <level>{message}</level>"
    PROCESS_DETAIL = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [{process.id}-{process.name}] [<level>{level: <8}</level>] - <cyan>{file}</cyan>:<cyan>{line}</cyan>[<cyan>{name}</cyan>:<cyan>{function}</cyan>] - <level>{message}</level>"
    PROCESS_SIMPLE = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> [{process.id}-{process.name}] [<level>{level: <8}</level>] - <level>{message}</level>"

    FILE_DETAIL = "{time:YYYY-MM-DD HH:mm:ss.SSS} [{level: <8}] | {name}:{line}[{function}] - {message}"

    PROCESS_FILE_DETAIL = "{time:YYYY-MM-DD HH:mm:ss.SSS} [{process.id}-{process.name}] [{level: <8}] | {name}:{line}[{function}] - {message}"


handlers = dict()


def set_logger(env: str, module_name: str, log_dir=None, log_path=None, show_process=False, function_name: str = None):
    """_summary_

    Args:
        env (str): environment: dev/test/prod
        log_dir (_type_, optional): target log dir. Defaults to None.

    Returns:
        _type_: loguru logger
    """
    env = env.strip().lower()
    # logger.info(f"setting logger for {module_name=}, {env=}, {log_dir=}, {log_path=}")
    if 0 in logger._core.handlers:
        logger.remove(0)
    if show_process:
        fmt = LoguruFormat.PROCESS_DETAIL if env in ["dev", "local"] else LoguruFormat.PROCESS_SIMPLE
    else:
        fmt = LoguruFormat.DETAIL if env in ["dev", "local"] else LoguruFormat.SIMPLE
    level = "DEBUG" if env in ["dev", "local"] else "INFO"
    retention = "7 days" if env in ["dev", "local"] else "30 days"

    def filter(r):
        if module_name and module_name not in r["name"]:
            return False
        if function_name and function_name not in r["function"]:
            return False
        return True

    def _add_handler(key, *args, **kwargs):
        if key in handlers:
            logger.info(f"handler:{key} already exists")
        else:
            handler_id = logger.add(*args, **kwargs)
            handlers[key] = handler_id
        logger.info(f"add handler{handler_id} for {key}")

    filter_key = module_name if module_name else function_name

    std_key = f"{filter_key}_stdout_{level}"

    _add_handler(std_key, sys.stdout, colorize=True, format=fmt, level=level, filter=filter, enqueue=True)

    file_fmt = LoguruFormat.PROCESS_FILE_DETAIL if show_process else LoguruFormat.FILE_DETAIL

    if log_path:
        _add_handler(f"{filter_key}_file_{level}_{log_path}", log_path, rotation="00:00", retention=retention,
                     enqueue=True, backtrace=True, level=level, filter=filter, format=file_fmt)
        logger.add(log_path, rotation="00:00", retention=retention, enqueue=True, backtrace=True, level=level, filter=filter, format=file_fmt)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        detail_log_path = os.path.join(log_dir, "detail.log")
        _add_handler(f"{filter_key}_file_DEBUG_{detail_log_path}", detail_log_path,  rotation="00:00", retention=retention, enqueue=True,
                     backtrace=True, level="DEBUG", filter=filter, format=file_fmt
                     )

        output_log_path = os.path.join(log_dir, "output.log")
        _add_handler(f"{filter_key}_file_INFO_{output_log_path}", output_log_path,  rotation="00:00", retention=retention, enqueue=True,
                     backtrace=True, level="INFO", filter=filter, format=file_fmt)
    return logger


def get_handler(module_name, sink_type):
    key = "_".join([module_name, sink_type])
    if key not in handlers:
        return None
    handler_id = handlers[key]
    handler = logger._core.handlers[handler_id]
    return handler


def update_level(module_name, sink_type, level):
    handler = get_handler(module_name, sink_type)
    level_no = logger.level(level).no
    # print(f"{level_no=}")
    handler._levelno = level_no


# 输出执行时长的包装器
class ChangeLogLevelContext(object):
    def __init__(self, module_name, sink_type, level):
        self.module_name = module_name
        self.level = level
        self.sink_type = sink_type
        self.handler = get_handler(module_name, sink_type)
        self.old_level = None

    def __enter__(self):
        if self.handler and self.level:
            self.old_level = self.handler._levelno
            level_no = logger.level(self.level).no
            # print(f"set log level :{level_no}")
            self.handler._levelno = level_no

    def __exit__(self, type, value, traceback):
        if self.handler and self.old_level:
            # print(f"restore log level :{self.old_level}")
            self.handler._levelno = self.old_level
