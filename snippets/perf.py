#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2024/03/07 10:53:50
@Author  :   ChenHao
@Description  : snippets for perf test
@Contact :   jerrychen1990@gmail.com
'''


import os
import time
import requests
from snippets.decorators import batch_process
from snippets.utils import create_dir_path, get_current_time_str, jdump, read2list
from loguru import logger


def default_build_req(item: dict) -> dict:
    return item


def default_build_resp(http_resp: dict) -> dict:
    return http_resp.json()["data"]


def req_http_service_detail(item, url, build_req_func=default_build_req, build_resp_func=default_build_resp) -> dict:
    st = time.time()

    req = build_req_func(item)
    resp = requests.post(url, json=req)
    resp.raise_for_status()
    resp = build_resp_func(resp)
    cost = time.time() - st
    rs = dict(item=item, req=req, resp=resp, cost=cost)
    return rs


def perf_test(input_path, url, req_func, output_path=None, work_num=1, max_num=None):
    logger.info("perf starts")
    logger.info(f"input_path: {input_path}, url:{url}, work_num:{work_num}")
    name, _ = os.path.splitext(input_path)
    if not output_path:
        output_path = os.path.join(
            name, f"{get_current_time_str()}.pef{work_num}.jsonl")
    create_dir_path(output_path)

    queries = read2list(input_path)
    st = time.time()
    if max_num:
        queries = queries[:max_num]

    func = batch_process(work_num=work_num, return_list=True)(req_func)
    rs = func(data=queries, url=url)
    # logger.info(rs)
    cost = time.time() - st
    costs = [e['cost'] for e in rs]
    latency = sum(costs)/len(costs)

    stat = dict(test_cost=cost, latency=latency, test_num=len(queries), qps=len(queries)/cost)
    # rs.append(stat)

    logger.info(f"dump to {output_path}")
    jdump(rs, output_path)
    logger.info(f"done")
    return rs, stat
