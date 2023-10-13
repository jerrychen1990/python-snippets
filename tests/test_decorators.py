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
import imp
import random
import unittest

from snippets.decorators import *


class TestUtils(unittest.TestCase):
    def test_adapt_single(self):
        @adapt_single(ele_name="data")
        def add1(data):
            # print(data)
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

    def test_multi_work(self):
        @batch_process(work_num=2)
        def add1(a):
            return a+1

        rs = add1(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        print(rs)

    def test_retry(self):
        @retry(retry_num=3, wait_time=0.1)
        def rand_func(a):
            if random.random() < a:
                print("success")
            else:
                raise Exception("fail")

        for i in range(5):
            try:
                rand_func(i/5)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    from time import sleep

    @retry(retry_num=3, wait_time=0.1)
    def rand_func(a):
        if random.random() < a:
            print("success")
        else:
            raise Exception("fail")

    for i in range(5):
        try:
            rand_func(i/5)
        except Exception as e:
            print(e)

    # @batch_process(work_num=3)
    # def add1(a, b=2):
    #     # print(f"{a}+{b}")
    #     sleep(1)
    #     return a+b

    # rs = add1(data=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], b=3)
    # print(rs)
    # print(list(rs))
