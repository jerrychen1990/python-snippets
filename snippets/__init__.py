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
SNIPPETS_ENV = os.environ.get("SNIPPETS_ENV", "prod")


from snippets.perf import *
from snippets.logs import *
from snippets.decorators import *
from snippets.utils import *
from snippets.mixin import *
from snippets.eval import *


logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d]:%(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S')
