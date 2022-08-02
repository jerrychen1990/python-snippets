# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setup
   Description :
   Author :       chenhao
   date：          2021/4/6
-------------------------------------------------
   Change Activity:
                   2021/4/6:
-------------------------------------------------
"""
from setuptools import setup, find_packages

REQ = [
    "tqdm",
    "pydantic"
]

setup(
    name='python-snippets',
    version='0.0.3',
    install_requires=REQ,
    packages=find_packages(exclude=['tests*']),
    package_dir={"": "."},
    package_data={},
    url='https://github.com/jerrychen1990/python-snippets.git',
    license='MIT',
    author='Chen Hao',
    author_email='jerrychen1990@gmail.com',
    zip_safe=True,
    description='useful python snippets',
    long_description="useful python snippets"
)
