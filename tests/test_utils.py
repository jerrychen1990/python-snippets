#! /usr/bin/env python3
# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     test_utils.py
   Author :       chenhao
   time：          2021/10/18 14:35
   Description :
-------------------------------------------------
"""
import unittest
from datetime import datetime
from snippets.utils import *
from typing import Union


class TestUtils(unittest.TestCase):
    def test_jdump(self):
        val = dict(a=12, b=12.13342352523, c="c", d=datetime.now())
        val_str = jdumps(val)
        logger.info(val_str)

    def test_groupby(self):
        l = [1, 1, 1, 2, 2, 3, 5, 5, 5, 1]
        g = groupby(l, map_func=lambda x: x ** 2)
        logger.info(g)
        g = groupby(l, sort_type="k", reverse=False)
        logger.info(g)

    def test_get_cur_dir(self):
        cur_path = get_cur_dir()
        logger.info(cur_path)

    def test_union_parse(self):
        class A(BaseModel):
            name: str

        class B(BaseModel):
            n: str

        C = Union[B, A]

        d = {"name": "name"}
        obj = union_parse_obj(C, d)
        logger.info(obj)
