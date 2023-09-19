#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/08/18 16:12:33
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import click

from snippets import execute_cmd


@click.command()
@click.argument('req')
def main(req):
    fails = []
    with open(req, 'r') as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                execute_cmd(f'pip install {line}')
            except Exception as e:
                fails.append(line)
                print(f"Failed to install {line}")
                print(e)
    print("Done!")
    if fails:
        print("Fails:")
        for fail in fails:
            print(fail)


if __name__ == "__main__":
    main()
