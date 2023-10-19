#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/16 14:09:07
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

from snippets.utils import jload
from typing import Union


class ConfigMixin:
    @classmethod
    def from_config(cls, config: Union[dict, str]):
        if isinstance(config, str):
            if config.endswith(".json"):
                config = jload(config)
            else:
                raise ValueError(f"{config} is not a valid config file")
        instance = cls(**config)
        return instance
