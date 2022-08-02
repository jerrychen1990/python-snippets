#! /usr/bin/env python3
# -*- coding utf-8 -*-
"""
-------------------------------------------------
   File Name：     utils.py
   Author :       chenhao
   time：          2021/10/14 17:41
   Description :
-------------------------------------------------
"""
import collections
import os
import json
import pickle
import subprocess
import time
import logging
from pydantic import BaseModel
from datetime import datetime

from typing import Any, List, Sequence, Tuple, Iterable, Dict, _GenericAlias

from tqdm import tqdm

logger = logging.getLogger(__name__)


# 创建一个目录
def create_dir_path(path: str):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


# 将一个object encode成json string的方法
class PythonObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return str(obj)
        if isinstance(obj, set):
            return list(obj)
        if isinstance(obj, BaseModel):
            return obj.dict(exclude_none=True, exclude_defaults=True)
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%M-%d %H:%m:%S")

        return {'_python_object': pickle.dumps(obj)}


# 将$obj转json string。默认ensure_ascii=False,并用indent=4展示
def jdumps(obj: Any, encoder=PythonObjectEncoder) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=4, cls=encoder)


# 将$obj转json string 写入$fp。$fp可以是一个文件路径，也可以是一个open函数打开的对象
def jdump(obj: Any, fp, encoder=PythonObjectEncoder):
    if isinstance(fp, str):
        create_dir_path(fp)
        with open(fp, mode='w', encoding="utf8") as fp:
            json.dump(obj, fp, ensure_ascii=False, indent=4, cls=encoder)
    else:
        json.dump(obj, fp, ensure_ascii=False, indent=4, cls=encoder)


# 将一个string的列表写入文件，常用于构造schema文件
def dump_lines(lines: List[str], fp):
    if isinstance(fp, str):
        fp = open(fp, mode="w", encoding="utf8")
    with fp:
        lines = [e + "\n" for e in lines]
        fp.writelines(lines)


# 将$obj转json-line string写入$fp。$fp可以是一个文件路径，也可以是一个open函数打开的对象
def jdump_lines(obj, fp, mode="w", progbar=False):
    iter_obj = tqdm(obj) if progbar else obj
    if isinstance(fp, str):
        create_dir_path(fp)
        fp = open(fp, mode=mode, encoding="utf8")
    with fp:
        for item in iter_obj:
            line = json.dumps(item, ensure_ascii=False, cls=PythonObjectEncoder) + "\n"
            fp.write(line)


# 将json string load成python object
def as_python_object(dct):
    if '_python_object' in dct:
        python_value = dct['_python_object']
        if isinstance(python_value, str):
            python_value = eval(python_value)
        return pickle.loads(python_value)
    return dct


# 将$fp的内容load成一个json对象。$fp可以是一个文件路径，也可以是一个open函数打开的对象
def jload(fp):
    if isinstance(fp, str):
        fp = open(fp, mode='r', encoding="utf8")
    with fp as fp:
        rs = json.load(fp, object_hook=as_python_object)
    return rs


# 将$s的内容load成一个json对象。
def jloads(s: str):
    return json.loads(s, object_hook=as_python_object)


# get a generator with from a jsonline file
def jload_lines(fp, max_data_num=None, return_generator=False):
    """
    将jsonline格式的文件转化成json object的generator。适用于文件过大，不想全部load到内存的时候
    Args:
        fp: 文件路径或者open之后的对象
        max_data_num: 最大load的数据条目数
        return_generator: 是否返回generator
    Returns: json object的generator
    """

    def get_gen(fp):
        if isinstance(fp, str):
            fp = open(fp, mode='r', encoding="utf8")
        idx = 0
        with fp as fp:
            for line in fp:
                if not line.strip():
                    continue
                yield jloads(line.strip())
                idx += 1
                if max_data_num and idx >= max_data_num:
                    break

    gen = get_gen(fp)
    if return_generator:
        gen
    return list(gen)


# 一行一行地读取文件内容
def load_lines(fp, return_generator=False):
    if isinstance(fp, str):
        create_dir_path(fp)
        fp = open(fp, mode="r", encoding="utf8")
    with fp:
        lines = fp.readlines()
        if return_generator:
            return (e.strip() for e in lines if e)
        return [e.strip() for e in lines if e]


# 递归将obj中的float做精度截断
def pretty_floats(obj, r=4):
    if isinstance(obj, float):
        return round(obj, r)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)
    return obj


# 将data batch化输出
def get_batched_data(data: Sequence, batch_size: int):
    batch = []
    for item in data:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


# 将$seq序列转化成下标到元素以及元素到下标的dict
def seq2dict(seq: Sequence) -> Tuple[dict, dict]:
    item2id = {item: idx for idx, item in enumerate(seq)}
    id2item = {idx: item for idx, item in enumerate(seq)}
    return item2id, id2item


# 得到$fmt格式化之后的当前时间字符串表示
def get_current_time_str(fmt="%Y-%m-%d-%H:%M:%S") -> str:
    rs = time.strftime(fmt, time.localtime())
    return rs


# 执行一个shell命令
def execute_cmd(cmd: str):
    logger.info("execute cmd:{}".format(cmd))
    status, output = subprocess.getstatusoutput(cmd)
    logger.info(f"status:{status}\noutput{output}")
    return status, output


# 将list of list 拍平成一个list
def flat(seq: Sequence[Iterable]) -> Iterable:
    if isinstance(seq, list):
        return [e for item in seq for e in item]
    else:
        return (e for item in seq for e in item)


# 将$seq序列聚合成dict。 key表示字典key生成的函数。 map_func表示字典value值的映射函数。
# 返回的字典会根据value序列长度倒序排序
def groupby(seq: Sequence, key=lambda x: x, map_func=lambda x: x,
            sort_type="v_len", reverse=True) -> Dict[Any, List]:
    rs_dict = collections.defaultdict(list)
    for i in seq:
        rs_dict[key(i)].append(map_func(i))

    def sort_func(x):
        if sort_type == "v_len":
            return len(x[1])
        if sort_type == "k":
            return x[0]
        return 0

    items = sorted(rs_dict.items(), key=sort_func, reverse=reverse)
    return collections.OrderedDict(items)


def star_surround_info(info: str, fix_length=128) -> str:
    star_num = max(fix_length - len(info), 2)
    left_star_num = star_num // 2
    right_star_num = star_num - left_star_num
    rs = "*" * left_star_num + info + "*" * right_star_num
    return rs

# # 将star_surround_info处理后的信息用logger或者print方法输出
def print_info(info, target_logger=None, fix_length=128):
    star_info = star_surround_info(info, fix_length)
    if target_logger:
        target_logger.info(star_info)
    else:
        print(star_info)

def get_cur_dir():
    return os.path.abspath(os.path.dirname(__file__))

def union_parse_obj(union:_GenericAlias, d:dict):
    for cls in union.__args__:
        try:
            obj = cls(**d)
            return obj
        except:
            pass
    raise Exception(f"fail to convert {d} to union {union}")





