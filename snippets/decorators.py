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
import os
import random
import time
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from typing import Generator, Iterable, List, Tuple

from tqdm import tqdm

from loguru import logger as default_logger


# 输出function执行耗时的函数
def log_cost_time(name=None, level="INFO", logger=None, star_len=0):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            with LogCostContext(name=name if name else func.__name__,
                                level=level, star_len=star_len, logger=logger):
                res = func(*args, **kwargs)
            return res

        return wrapped

    return wrapper

# 输出执行时长的包装器
class LogCostContext(object):
    def __init__(self, name, level="INFO", logger=None, star_len=0):
        self.name = name
        self.level = level
        self.star_len = star_len
        self.logger = logger if logger else default_logger

    def __enter__(self):
        msg = f"{self.name} starts"
        half_star_len = max((self.star_len - len(msg)) // 2, 0)
        msg = "*" * half_star_len + msg + "*" * half_star_len
        self.logger.log(self.level, msg)
        self.st = time.time()

    def __exit__(self, type, value, traceback):
        cost = time.time() - self.st
        msg = f"{self.name} ends, cost:{cost:4.3f} seconds"
        half_star_len = max((self.star_len - len(msg)) // 2, 0)
        msg = "*" * half_star_len + msg + "*" * half_star_len
        self.logger.log(self.level, msg)


# 执行函数时输出函数的参数以及返回值
def log_function_info(input_level="DEBUG", result_level="DEBUG",
                      exclude_self=True):

    def wrapper(func):
        def wrapped_func(*args, **kwargs):
            if input_level:
                show_args = args
                if exclude_self and len(args) > 1:
                    show_args = args[1:]
                msg = f"call function:{func} with\n args:{show_args}\n kwargs:{kwargs}"
                default_logger.log(input_level, msg)

            res = func(*args, **kwargs)
            if result_level:
                msg = f"function:{func} return with:\n{res}"
                default_logger.log(result_level, msg)
            return res

        return wrapped_func

    return wrapper


# 确保参数中path的文件所在的目录存在，不存在则创建一个
def ensure_file_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        path = kwargs['path']
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

    return wrapper


# 确保参数中path目录存在，不存在则创建一个
def ensure_dir_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        dir_path = kwargs['path']
        os.makedirs(dir_path, exist_ok=True)
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
def adapt_single(ele_name:str):
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

# 自动加上重试功能
def retry(retry_num: int, wait_time: float | tuple[float, float], level="INFO"):
    def wrapper(func):
        @wraps(func)
        def wrapped(*args, **kwargs):
            num_left = retry_num

            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if num_left == 0:
                        default_logger.warning("no attempts left, throw exception")
                        default_logger.exception(e)
                        raise e
                    if isinstance(wait_time, tuple):
                        wt = random.uniform(wait_time[0], wait_time[1])
                    else:
                        wt = wait_time

                    default_logger.log(level, f'retry {func.__name__}, {num_left} attempts left, sleep:{wt:2.3f} seconds')
                    time.sleep(wt)
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
            total = None if not hasattr(data, '__len__') else len(data)
            rs = tqdm(rs_iter, total=total)
            if return_list:
                return list(rs)
            return rs
        return wrapped
    return wrapper
