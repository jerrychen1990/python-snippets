#! /usr/bin/env python3
# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     __init__.py.py
   Author :       chenhao
   time：          2021/10/18 14:34
   Description :
-------------------------------------------------
"""
import logging

from snippets.utils import *
from snippets.decorators import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
