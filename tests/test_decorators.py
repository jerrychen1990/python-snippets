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
