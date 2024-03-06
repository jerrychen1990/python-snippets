#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/13 15:38:27
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''

import time
import requests
from loguru import logger
from snippets.decorators import batch_process
from snippets.utils import get_current_time_str, jdump, jload_lines
import click


def default_build_req(item:dict)->dict:
    return item
    
def default_build_resp(http_resp:dict)->dict:
    return http_resp.json()["data"]



def pef_test(url, item, build_req_func = default_build_req, build_resp_func = default_build_resp):
    st = time.time()
    
    req = build_req_func(item)
    resp = requests.post(url, json=req)
    resp.raise_for_status()
    resp = default_build_resp(resp)
    cost = time.time() - st
    rs = dict(item=item, req=req, resp=resp, cost=cost)
    return rs
    
    
@click.command()
@click.option("--input_path")
@click.option("--work_num", default=1)
@click.option("--url")
def main(input_path,url,  work_num=1):
    logger.info("perf starts")
    logger.info(f"input_path: {input_path}, url:{url}, work_num:{work_num}")
    
    output_path = input_path.replace(".jsonl", f"{get_current_time_str}.pef{work_num}.jsonl")
    queries = jload_lines(input_path)
    st = time.time()
    queries = queries[:]

    func = batch_process(work_num=work_num, return_list=True)(pef_test)
    rs = func(data=queries, url=url)
    # logger.info(rs)
    cost = time.time() - st

    stat=dict(test_cost=cost, test_num=len(queries), qps=len(queries)/cost)
    rs.append(stat)

    logger.info(f"dump to {output_path}")
    jdump(rs, output_path)
    logger.info(f"done")

    
if __name__ == "__main__":
    main()
