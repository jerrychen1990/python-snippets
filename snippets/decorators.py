#! /usr/bin/env python3
# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     decorators.py
   Author :       chenhao
   time：          2021/10/18 11:32
   Description :
-------------------------------------------------
"""
import inspect
import logging
import time
import os
from functools import wraps

logger = logging.getLogger(__name__)


# 输出function执行耗时的函数
def log_cost_time(name=None, level=logging.INFO):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with LogCostContext(name=name if name else func.__name__, level=level):
                res = func(*args, **kwargs)
            return res

        return wrapped

    return wrapper


class LogCostContext(object):
    def __init__(self, name, level=logging.INFO):
        self.name = name
        self.level = level

    def __enter__(self):
        logger.log(msg=f"{self.name} starts", level=self.level)
        self.st = time.time()

    def __exit__(self, type, value, traceback):
        cost = time.time() - self.st
        logger.log(msg=f"{self.name} ends, cost:{cost:4.3f} seconds", level=self.level)


# 执行函数时输出函数的参数以及返回值
def log_function_info(input_level=logging.DEBUG, result_level=logging.DEBUG,
                      exclude_self=True):
    def wrapper(func):
        def wrapped_func(*args, **kwargs):
            if input_level:
                show_args = args
                if exclude_self and len(args) > 1:
                    show_args = args[1:]
                msg = f"call function:{func} with\n args:{show_args}\n kwargs:{kwargs}"
                logger.log(level=input_level, msg=msg)

            res = func(*args, **kwargs)
            if result_level:
                msg = f"function:{func} return with:\n{res}"
                logger.log(level=result_level, msg=msg)
            return res

        return wrapped_func

    return wrapper


# 确保参数中path的文件所在的目录存在，不存在则创建一个
def ensure_file_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        path = kwargs['path']
        dir_path = os.path.dirname(path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return func(*args, **kwargs)

    return wrapper


# 确保参数中path目录存在，不存在则创建一个
def ensure_dir_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        dir_path = kwargs['path']
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return func(*args, **kwargs)

    return wrapper


# 忽略过多的kwarg参数
def discard_kwarg(func):
    arg_names = inspect.signature(func).parameters.keys()

    def wrap(*args, **kwargs):
        kwargs = {k: v for k, v in kwargs.items() if k in arg_names}
        return func(*args, **kwargs)

    return wrap
