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
from typing import Union

from snippets.utils import *


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
        cur_path = os.path.abspath(os.path.dirname(__file__))
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

    def test_get_next_version(self):
        version = "v1.0.0"
        self.assertEqual("v1.0.1", get_next_version(version))
        self.assertEqual("v2.0.0", get_next_version(version, 2))

    def test_get_latest_version(self):
        latest_version = get_latest_version("python-snippets")
        print(latest_version)

    def test_deep_update(self):
        origin = dict(a=1, b=dict(c=1), c="c")
        to_update = dict(a=2, b=dict(e=2), c=dict(f="f"), k="k")
        updated = deep_update(origin, to_update, inplace=False)
        print(updated)
        print(origin)
        self.assertEquals(updated, {'a': 2, 'b': {'c': 1, 'e': 2}, 'c': {'f': 'f'}, 'k': 'k'})
        self.assertEquals(origin, {'a': 1, 'b': {'c': 1}, 'c': 'c'})

    def test_load(self):
        data = load("data/sample.*")
        print(len(data))
        self.assertEquals(len(data), 6)

    def test_cache_load(self):
        file_path = "data/sample.jsonl"
        data = load_with_cache(file_path)
        print(len(data))
        self.assertEquals(len(data), 3)
        data = load_with_cache(file_path)
        print(len(data))

    def test_batch_process_with_save(self):
        data = range(20)
        def func(x): return (e**2 for e in x)
        dist_path = "./batch_process_result.txt"
        batch_process_with_save(data, func, dist_path, batch_size=6)
        if os.path.exists(dist_path):
            os.remove(dist_path)
