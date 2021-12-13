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
    version='0.0.1',
    install_requires=REQ,
    packages=find_packages(exclude=['tests*']),
    package_dir={"": "."},
    package_data={},
    url='https://github.com/jerrychen1990/snippets.git',
    license='MIT Licence',
    author='Chen Hao',
    author_email='jerrychen1990@gmail.com',
    zip_safe=True,
    description='useful python python-snippets',
)
