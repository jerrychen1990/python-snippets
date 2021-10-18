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
from snippets.utils import *


class TestUtils(unittest.TestCase):
    def test_jdump(self):
        val = dict(a=12, b=12.13342352523, c="c")
        val_str = jdumps(val)
        logger.info(val_str)
