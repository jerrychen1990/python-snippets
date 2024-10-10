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

import os

from snippets.decorators import *
from snippets.evaluate import *
from snippets.logs import *
from snippets.mixin import *
from snippets.perf import *
from snippets.utils import *

__version__ = "0.1.3"

SNIPPETS_ENV = os.environ.get("SNIPPETS_ENV", "prod")
logger = set_logger(SNIPPETS_ENV, __name__)
