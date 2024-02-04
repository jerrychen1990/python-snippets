#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@Time    :   2023/10/19 18:13:06
@Author  :   ChenHao
@Contact :   jerrychen1990@gmail.com
'''


from snippets.utils import groupby

# 计算f1
def get_f1(precision, recall):
    f1 = 0. if precision + recall == 0 else 2 * \
        precision * recall / (precision + recall)
    return f1


# 获得precision和recall值
def get_pr(tp, fp, fn):
    precision = 0. if tp + fp == 0 else tp / (tp + fp)
    recall = 0. if tp + fn == 0 else tp / (tp + fn)
    return dict(precision=precision, recall=recall)


# 获得tp,fp,fn集合
def get_tp_fp_fn_set(true_set, pred_set):
    tp_set = true_set & pred_set
    fp_set = pred_set - tp_set
    fn_set = true_set - tp_set
    return tp_set, fp_set, fn_set


# 测评两个集合
def eval_sets(true_set, pred_set):
    tp_set, fp_set, fn_set = get_tp_fp_fn_set(true_set, pred_set)
    tp = len(tp_set)
    fp = len(fp_set)
    fn = len(fn_set)
    rs_dict = dict(tp=tp, fp=fp, fn=fn)
    pr_dict = get_pr(tp, fp, fn)
    rs_dict.update(**pr_dict)
    rs_dict.update(f1=get_f1(rs_dict['precision'], rs_dict['recall']))

    return rs_dict


def get_micro_avg(set_eval_list):
    tp = sum(e['tp'] for e in set_eval_list)
    fp = sum(e['fp'] for e in set_eval_list)
    fn = sum(e['fn'] for e in set_eval_list)
    rs_dict = dict(tp=tp, fp=fp, fn=fn)
    pr_dict = get_pr(tp, fp, fn)
    rs_dict.update(**pr_dict)
    rs_dict.update(f1=get_f1(rs_dict['precision'], rs_dict['recall']))
    return rs_dict


def get_macro_avg(set_eval_list):
    precision_list = [e['precision']
                      for e in set_eval_list if e['tp'] + e['fp'] > 0]
    recall_list = [e['recall'] for e in set_eval_list if e['tp'] + e['fn'] > 0]
    precision = sum(precision_list) / \
        len(precision_list) if precision_list else 0.
    recall = sum(recall_list) / len(recall_list) if recall_list else 0.
    f1 = get_f1(precision, recall)
    rs_dict = dict(precision=precision, recall=recall, f1=f1)
    return rs_dict


def pr_statistic(true_sets, pred_sets):

    true_label_dict = groupby(true_sets, key=lambda x: x[1])
    pred_label_dict = groupby(pred_sets, key=lambda x: x[1])

    target_type_set = true_label_dict.keys() | pred_label_dict.keys()
    detail_dict = dict()
    for target_type in target_type_set:
        true_list = true_label_dict.get(target_type, [])
        true_set = set(true_list)
        pred_list = pred_label_dict.get(target_type, [])
        pred_set = set(pred_list)
        eval_rs = eval_sets(true_set, pred_set)
        detail_dict[target_type] = eval_rs
    detail_dict = dict(
        sorted(detail_dict.items(), key=lambda x: x[1]["f1"], reverse=True))
    set_eval_list = detail_dict.values()
    micro_eval_rs = get_micro_avg(set_eval_list)
    macro_eval_rs = get_macro_avg(set_eval_list)
    rs_dict = dict(detail=detail_dict, micro=micro_eval_rs,
                   macro=macro_eval_rs)
    return rs_dict
