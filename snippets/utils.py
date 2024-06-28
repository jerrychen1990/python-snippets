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
import copy
import glob
import json
import os
import pickle
import re
import shutil
import subprocess
import time

from datetime import datetime
from cachetools import LRUCache, cached
import pandas as pd
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple, _GenericAlias, Union

import numpy as np
from pydantic import BaseModel
from tqdm import tqdm
from loguru import logger


# 创建一个目录
def create_dir_path(path: str):
    dir_path = os.path.abspath(os.path.dirname(path))
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
            return obj.model_dump(exclude_none=True, exclude_defaults=True)
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%M-%d %H:%m:%S")
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            try:
                return str(obj)
            except Exception as e:
                return super().default(obj)


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
        lines = [str(e) + "\n" for e in lines]
        fp.writelines(lines)


# 将$obj转json-line string写入$fp。$fp可以是一个文件路径，也可以是一个open函数打开的对象
def jdump_lines(obj, fp, mode="w", progbar=False):
    iter_obj = tqdm(obj) if progbar else obj
    if isinstance(fp, str):
        create_dir_path(fp)
        fp = open(fp, mode=mode, encoding="utf8")
    with fp:
        for item in iter_obj:
            line = json.dumps(item, ensure_ascii=False,
                              cls=PythonObjectEncoder) + "\n"
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

    def get_gen(f):
        if isinstance(f, str):
            f = open(f, mode='r', encoding="utf8")
        idx = 0
        with f as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                yield jloads(line)
                idx += 1
                if max_data_num and idx >= max_data_num:
                    break

    gen = get_gen(fp)
    if return_generator:
        return gen
    return list(gen)

# table类的文件转化为list of dict


def table2json(path, **kwargs):
    if path.endswith("csv"):
        df = pd.read_csv(path, **kwargs)
    if path.endswith("xlsx"):
        df = pd.read_excel(path, **kwargs)
    df.replace(np.nan, None, inplace=True)
    cols = df.columns.tolist()
    cols = [e for e in cols if not e.startswith("Unnamed")]
    df = df[cols]
    records = df.to_dict(orient="records")
    return records


# 将list数据存储成table格式
def dump2table(data, path: str):
    if isinstance(data, list):
        data = pd.DataFrame.from_records(data)
    assert isinstance(data, pd.DataFrame)
    df = data
    if path.endswith(".csv"):
        df.to_csv(path, index=False)
    elif path.endswith(".xlsx"):
        df.to_excel(path, index=False)
    else:
        raise Exception(f"Unknown file format: {path}")


# 一行一行地读取文件内容
def load_lines(fp, return_generator=False):
    if isinstance(fp, str):
        fp = open(fp, mode="r", encoding="utf8")
    with fp:
        lines = fp.readlines()
        if return_generator:
            return (e.strip() for e in lines if e)
        return [e.strip() for e in lines if e]

# 根据后缀名读取list数据


def read2list(file_path: Union[str, List], **kwargs) -> List[Union[str, dict]]:

    def _read2list(file_path, **kwargs):
        suffix = os.path.splitext(file_path)[-1].lower()
        if suffix == ".json":
            return jload(file_path, **kwargs)
        if suffix == ".jsonl":
            return jload_lines(file_path, **kwargs)
        if suffix in [".xlsx", ".csv"]:
            return table2json(file_path, **kwargs)
        if suffix in [".txt"]:
            return load_lines(file_path, **kwargs)
        else:
            logger.warning(f"unknown suffix:{suffix}, read as txt")
            return load_lines(file_path, **kwargs)
    if isinstance(file_path, str):
        file_path = glob.glob(file_path) if "*" in file_path else [file_path]

    rs = []
    for f in file_path:
        # logger.info(f"reading file_path={f}")
        tmp = _read2list(f, **kwargs)
        if isinstance(tmp, list):
            rs.extend(tmp)
        else:
            rs.append(tmp)
    if len(file_path) == 1 and len(rs) == 1 and file_path[0].endswith(".json"):
        rs = rs[0]

    return rs


# 将list数据按照后缀名格式dump到文件
def dump2list(data: List, file_path: str, **kwargs):
    create_dir_path(file_path)
    suffix = os.path.splitext(file_path)[-1].lower()
    if suffix == ".json":
        return jdump(data, file_path, **kwargs)
    if suffix == ".jsonl":
        return jdump_lines(data, file_path, **kwargs)
    if suffix in [".xlsx", ".csv"]:
        return dump2table(data, file_path)
    if suffix in [".txt"]:
        return dump_lines(data, file_path, **kwargs)
    else:
        logger.warning(f"unknown suffix:{suffix}, dump as txt")
        return dump_lines(data, file_path, **kwargs)


dump_list = dump2list
load2list = read2list

dump = dump2list
load = read2list


@cached(cache=LRUCache(10))
def _load_with_cache(file_path, last_modified_time, **kwargs):
    dt_object = datetime.fromtimestamp(last_modified_time)
    last_modified_time = dt_object.strftime("%Y-%m-%d %H:%M:%S")
    logger.debug(f"loading file:{file_path} with {last_modified_time=}, {kwargs=}")
    data = load(file_path, **kwargs)
    return data


def load_with_cache(file_path, **kwargs):
    last_modified_time = os.path.getmtime(file_path)
    return _load_with_cache(file_path, last_modified_time, **kwargs)


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
def get_batched_data(data: Iterable, batch_size: int) -> Iterable[List]:
    """将数据按照batch_size分组

    Args:
        data (Iterable): 待分组数据
        batch_size (int): 分组大小

    Yields:
        _type_: batch数据
    """
    batch = []
    for item in data:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


batchify = get_batched_data

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
def groupby(seq: Sequence, key=lambda x: x, map_func=lambda x: x, reduce_func=None,
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
    if reduce_func:
        items = [(k, reduce_func(v)) for k, v in items]
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

# 把一个dict转化到一个Union类型


def union_parse_obj(union: _GenericAlias, d: dict):
    for cls in union.__args__:
        try:
            obj = cls(**d)
            return obj
        except:
            pass
    raise Exception(f"fail to convert {d} to union {union}")

# 获取一个包的最新version


def get_latest_version(package_name: str) -> str:
    cmd = f"pip install {package_name}=="
    status, output = execute_cmd(cmd)
    pattern = "\(from versions:(.*?)\)"

    for item in re.findall(pattern, output):
        if item is None:
            return "0.0.1"

        # item
        versions = [tuple(int(i) for i in e.strip().split("."))
                    for e in item.split(",")]
        # versions
        latest_version = max(versions)
        latest_version = ".".join(str(i) for i in latest_version)
        return latest_version

# 获取一个version的下一个版本


def get_next_version(version: str, level=0) -> str:
    pieces = version.split(".")
    idx = len(pieces) - level - 1
    val = pieces[idx]
    if val.startswith("v"):
        pieces[idx] = "v" + str(int(val[1])+1)
    else:
        pieces[idx] = str(int(val)+1)
    return ".".join(pieces)


def deep_update(origin: dict, new_data: dict, inplace=True) -> dict:
    """递归跟新dict

    Args:
        origin (dict): 原始dict
        new_data (dict): 需要更新的数据
        inplace (bool, optional): 是否在原dict上直接修改. Defaults to True.

    Returns:
        dict: 更新后的dict
    """
    to_update = origin if inplace else copy.deepcopy(origin)

    def _deep_update_inplace(tu: dict, nd: dict) -> dict:
        for k, v in nd.items():
            if k not in to_update:
                tu[k] = v
            else:
                if isinstance(v, dict) and isinstance(to_update[k], dict):
                    _deep_update_inplace(to_update[k], v)
                else:
                    tu[k] = v
        return tu
    return _deep_update_inplace(to_update, new_data)


def delete_paths(paths: str | List[str]):
    if isinstance(paths, str):
        paths = [paths]
    for path in paths:
        try:
            if os.path.isfile(path):  # Check if it's a file
                os.remove(path)
                # print(f"File {path} has been deleted.")
            elif os.path.isdir(path):  # Check if it's a directory
                shutil.rmtree(path)
                # print(f"Directory {path} has been deleted.")
            else:
                pass
                # print(f"No such file or directory: {path}")
        except Exception as e:
            raise e
            # logger.exception("e")


def batch_process_with_save(data: Iterable, func: Callable, file_path: str, batch_size: int, **kwargs):
    """将数据按照指定函数dump到文件

    Args:
        data (Iterable): 待dump数据
        func (Callable): dump函数
        file_path (str): 文件路径
        **kwargs: dump函数参数
    """
    stem, suffix = os.path.splitext(file_path)
    history_files = glob.glob(f"{stem}-[0-9]*-[0-9]*.{suffix}")
    acc = load(history_files)

    logger.info(f"{len(acc)} history data loaded")
    # logger.info(history_files)
    data = data[len(acc):]

    for idx, batch in enumerate(batchify(data, batch_size)):
        batch_result = list(func(batch, **kwargs))
        dump(batch_result, f"{stem}-{idx*batch_size}-{idx*batch_size+len(batch)}.{suffix}")
        acc.extend(batch_result)

    history_files = glob.glob(f"{stem}*.{suffix}")
    delete_paths(history_files)
    logger.info(f"dump {len(acc)} items to {file_path}")
    dump(acc, file_path)
    return acc
    # logger.info(history_files)
