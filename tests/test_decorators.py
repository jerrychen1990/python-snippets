#! /usr/bin/env python3
# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_decorators.py
   Author :       chenhao
   time：          2021/10/18 14:35
   Description :
-------------------------------------------------
"""

import random
import unittest

from loguru import logger

from snippets.decorators import *


def add(a, b=1, sleep=False):
    if sleep:
        logger.info(f"sleep {a} seconds")
        time.sleep(a)

    return a + b


def sleep_with_add(a):
    return add(a, sleep=True)


class TestUtils(unittest.TestCase):
    def test_adapt_single(self):
        @adapt_single(ele_name="data")
        def add1(data):
            # logger.info(data)
            return [e["data"] + 1 if isinstance(e, dict) else e + 1 for e in data]

        batch_rs = add1(data=[1, 2, 3])
        self.assertEqual([2, 3, 4], batch_rs)

        batch_rs = add1(data=(1, 2, 3))
        self.assertEqual([2, 3, 4], batch_rs)

        batch_rs = add1(data=(e for e in range(1, 4)))
        self.assertEqual([2, 3, 4], batch_rs)

        single_rs = add1(data=1)
        self.assertEqual(2, single_rs)

        single_rs = add1(data=dict(data=1))
        self.assertEqual(2, single_rs)

    def test_log_cost(self):
        @log_cost_time(star_len=40)
        def sleep_add(a, b):
            time.sleep(random.random())
            return a + b

        sleep_add(1, 2)

    async def test_async_decorator(self):
        def func(x):
            return x**2

        rs = func(4)
        logger.info(rs)
        self.assertEqual(16, rs)

        func = asyncify(func)
        rs = await func(4)
        logger.info(rs)
        self.assertEqual(16, rs)

    def test_multi_thread(self):
        fn = batch_process(work_num=2, return_list=False)(add)
        rs = fn(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], b=2, sleep=True)
        rs_list = []
        for e in rs:
            logger.info(e)
            rs_list.append(e)
        self.assertListEqual([3, 4, 5, 6, 7, 8, 9, 10, 11, 12], rs_list)

    def test_multi_process(self):
        process_batch_fn = multi_process(work_num=4, return_list=True)(sleep_with_add)
        rs = process_batch_fn(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        logger.info(rs)
        self.assertListEqual([2, 3, 4, 5, 6, 7, 8, 9, 10, 11], rs)

    def test_retry(self):
        @retry(retry_num=3, wait_time=(0.1, 0.4))
        def rand_func(a):
            if random.random() < a:
                logger.info("success")
            else:
                raise Exception("fail")

        for i in range(5):
            try:
                rand_func(i / 5)
            except Exception as e:
                logger.info(e)


if __name__ == "__main__":
    unittest.main()
