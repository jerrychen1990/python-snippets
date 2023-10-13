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
import os
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Generator, Iterable, List, Tuple, Union

from tqdm import tqdm

from snippets.utils import jload

default_logger = logging.getLogger(__file__)
default_logger.setLevel(logging.DEBUG)


# 输出function执行耗时的函数
def log_cost_time(name=None, level=logging.INFO, logger=None, star_len=0):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with LogCostContext(name=name if name else func.__name__,
                                level=level, star_len=star_len, logger=logger):
                res = func(*args, **kwargs)
            return res

        return wrapped

    return wrapper


class LogCostContext(object):
    def __init__(self, name, level=logging.INFO, logger=None, star_len=0):
        self.name = name
        self.level = level
        self.star_len = star_len
        self.logger = logger if logger else default_logger

    def __enter__(self):
        msg = f"{self.name} starts"
        half_star_len = max((self.star_len - len(msg)) // 2, 0)
        msg = "*" * half_star_len + msg + "*" * half_star_len
        self.logger.log(msg=msg, level=self.level)
        self.st = time.time()

    def __exit__(self, type, value, traceback):
        cost = time.time() - self.st
        msg = f"{self.name} ends, cost:{cost:4.3f} seconds"
        half_star_len = max((self.star_len - len(msg)) // 2, 0)
        msg = "*" * half_star_len + msg + "*" * half_star_len
        self.logger.log(msg=msg, level=self.level)


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
                default_logger.log(level=input_level, msg=msg)

            res = func(*args, **kwargs)
            if result_level:
                msg = f"function:{func} return with:\n{res}"
                default_logger.log(level=result_level, msg=msg)
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


# adapt function with single elements
def adapt_single(ele_name):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            if ele_name in kwargs:
                is_single = not isinstance(
                    kwargs[ele_name], (List, Generator, Tuple))
            else:
                is_single = False
            if is_single:
                kwargs[ele_name] = [kwargs[ele_name]]
            rs = func(*args, **kwargs)
            if is_single:
                rs = rs[0]
            return rs
        return wrapped
    return wrapper


def retry(retry_num, wait_time, level=logging.INFO):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            num_left = retry_num

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if num_left == 0:
                        raise e
                    time.sleep(wait_time)
                    default_logger.log(
                        level, f'retry {func.__name__}, {num_left} retry left')
                    num_left -= 1
        return wrapped
    return wrapper


# 线程池批量跑function
def batch_process(work_num, return_list=False):
    def wrapper(func):
        @wraps(func)
        def wrapped(data: Iterable, *args, **kwargs):
            # add a thread pool here
            executors = ThreadPoolExecutor(work_num)

            def _func(x):
                return func(x, *args, **kwargs)
            rs_iter = executors.map(_func, data)
            rs = tqdm(rs_iter)
            if return_list:
                return list(rs)
            return rs
        return wrapped
    return wrapper


class ConfigMixin:
    @classmethod
    def from_config(cls, config: Union[dict, str]):
        if isinstance(config, str):
            if config.endswith(".json"):
                config = jload(config)
            else:
                raise ValueError(f"{config} is not a valid config file")
        instance = cls(**config)
        return instance
