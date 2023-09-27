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
import sys

from setuptools import find_packages, setup

from snippets.utils import get_latest_version, get_next_version

REQ = [
    "tqdm",
    "pydantic",
    "numpy",
    "click"
]


if __name__ == "__main__":
    name = "python-snippets"
    if len(sys.argv) >= 4 and sys.argv[-1].startswith("v"):
        version = sys.argv.pop(-1)
    else:
        latest_version = get_latest_version(name)
        version = get_next_version(latest_version)
    print(f"version: {version}")

    setup(
        name=name,
        version=version,
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
