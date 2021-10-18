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
def log_cost_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_timestamp = time.time()
        res = func(*args, **kwargs)
        end_timestamp = time.time()
        cost = end_timestamp - start_timestamp
        logger.info(f"function:{func.__name__} cost:{cost:4.3f} seconds")
        return res

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