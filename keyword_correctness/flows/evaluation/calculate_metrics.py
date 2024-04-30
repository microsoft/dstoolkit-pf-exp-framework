from typing import List

from promptflow import log_metric, tool
from collections import defaultdict
import pandas as pd
import numpy as np
import re


@tool
def calculate_metrics(grades: List[dict]):
    metrics_dict = {}
    eval_df = pd.DataFrame(grades)
    #### errors metrics
    # get count of FSNs in dataset
    fsn_count = len(eval_df)
    # count FSNs with big parsing error
    fsn_big_parse_error_count = sum(eval_df["pred_big_parse_error"])
    # count FSNs with at least 1 error while parsing keyword predictions
    fsn_small_pred_error_count = sum(eval_df["pred_small_parse_errors_count"]>0)
    # add metrics on fsn level
    metrics_dict["pred_big_parse_errors_count"] = fsn_big_parse_error_count
    metrics_dict["pred_big_parse_errors_ratio"] = fsn_big_parse_error_count / fsn_count
    metrics_dict["fsn_pred_small_parse_errors_count"] = fsn_small_pred_error_count
    metrics_dict["fsn_pred_small_parse_errors_ratio"] =  fsn_small_pred_error_count / fsn_count

    # track errors on total keywords level
    total_keywords_count = sum(eval_df["keyword_count"])
    total_small_pred_error_count = sum(eval_df["pred_small_parse_errors_count"])
    metrics_dict["total_pred_small_parse_errors_count"] = total_small_pred_error_count
    metrics_dict["total_pred_small_parse_errors_ratio"] = total_small_pred_error_count / total_keywords_count

    #### DS metrics
    # filter FSN where any errors occured
    eval_df_no_errors = eval_df.loc[(eval_df["pred_big_parse_error"]==0) & (eval_df["pred_small_parse_errors_count"]==0)]
    if len(eval_df_no_errors) > 0:
        # calc metrics only if valid rows are present
        metrics_dict = metrics_dict | get_best_metrics_by_threshold(eval_df_no_errors)
        best_threshold = metrics_dict["threshold"]

        # PROXY IMPACT METRICS
        eval_df_no_errors["catalog_unique_tokens"] = eval_df_no_errors["ground_truth"].apply(
            lambda x: get_unique_tokens(" ".join(x.keys()))
        )
        eval_df_no_errors["true_unique_tokens"] = eval_df_no_errors["ground_truth"].apply(
            lambda x: get_unique_tokens(" ".join(
                [k for k, v in x.items() if v=="correct"]))
        )
        eval_df_no_errors["pred_unique_tokens"] = eval_df_no_errors["predictions"].apply(
            lambda x: get_unique_tokens(" ".join(
                [p["keyword"] for p in x if p["result"]>=best_threshold]))
        )
        eval_df_no_errors["top3_overlap_tokens_vs_catalog"] = eval_df_no_errors[["catalog_unique_tokens", "pred_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:3], x[1][:3]), axis=1)
        eval_df_no_errors["top7_overlap_tokens_vs_catalog"] = eval_df_no_errors[["catalog_unique_tokens", "pred_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:7], x[1][:7]), axis=1)
        
        eval_df_no_errors["top3_overlap_tokens_vs_gt"] = eval_df_no_errors[["true_unique_tokens", "pred_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:3], x[1][:3]), axis=1)
        eval_df_no_errors["top7_overlap_tokens_vs_gt"] = eval_df_no_errors[["true_unique_tokens", "pred_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:7], x[1][:7]), axis=1)
        
        eval_df_no_errors["top3_overlap_tokens_vs_gt_all"] = eval_df_no_errors[["pred_unique_tokens", "true_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:3], x[1]), axis=1)
        eval_df_no_errors["top7_overlap_tokens_vs_gt_all"] = eval_df_no_errors[["pred_unique_tokens", "true_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:7], x[1]), axis=1)
        
        eval_df_no_errors["top3_overlap_tokens_catalog_vs_gt"] = eval_df_no_errors[["catalog_unique_tokens", "true_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:3], x[1][:3]), axis=1)
        eval_df_no_errors["top7_overlap_tokens_catalog_vs_gt"] = eval_df_no_errors[["catalog_unique_tokens", "true_unique_tokens"]].apply(
            lambda x: calc_overlap_of_correct(x[0][:7], x[1][:7]), axis=1)
        
        metrics_dict = metrics_dict | {
            "top3_overlap_tokens_vs_catalog": eval_df_no_errors["top3_overlap_tokens_vs_catalog"].mean(),
            "top7_overlap_tokens_vs_catalog": eval_df_no_errors["top7_overlap_tokens_vs_catalog"].mean(),
            "top3_overlap_tokens_vs_gt": eval_df_no_errors["top3_overlap_tokens_vs_gt"].mean(),
            "top7_overlap_tokens_vs_gt": eval_df_no_errors["top7_overlap_tokens_vs_gt"].mean(),
            "top3_overlap_tokens_vs_gt_all": eval_df_no_errors["top3_overlap_tokens_vs_gt_all"].mean(),
            "top7_overlap_tokens_vs_gt_all": eval_df_no_errors["top7_overlap_tokens_vs_gt_all"].mean(),
            "top3_overlap_tokens_catalog_vs_gt": eval_df_no_errors["top3_overlap_tokens_catalog_vs_gt"].mean(),
            "top7_overlap_tokens_catalog_vs_gt": eval_df_no_errors["top7_overlap_tokens_catalog_vs_gt"].mean(),
            "top3_hit_rate": sum(eval_df_no_errors["top3_overlap_tokens_vs_gt"]>0.0) / len(eval_df_no_errors),
            "top7_hit_rate": sum(eval_df_no_errors["top7_overlap_tokens_vs_gt"]>0.0) / len(eval_df_no_errors),
        }

    # log all metrics in promptflow
    # you can only log float values so we can't log arrays of metrics for different thresholds
    for metric, v in metrics_dict.items():
        log_metric(metric, v)

    # for vertical metrics analysis
    list_of_metrics = ["accuracy", "recall_incorrect", "recall_correct", "precision_incorrect", "precision_correct", "f1_incorrect", "f1_correct"]
    # Macro, collect FSN-level metrics and average across all FSNs
    for metric in list_of_metrics:  
        # default threshold metrics
        metrics_dict["macro_%s_default" % metric] = eval_df_no_errors[metric].mean()

    # Micro/Collect all keywords and calculate metrics from that level
    # get confusion matrix for all keywords
    TP, TN, FP, FN = [sum(eval_df_no_errors[k]) for k in ["true_positive", "true_negative", "false_positive", "false_negative"]]
    metrics_dict["TP_default"] = TP
    metrics_dict["FP_default"] = FP
    metrics_dict["TN_default"] = TN
    metrics_dict["FN_default"] = FN
    # calculate metrics based on confusion matrix info
    metrics_dict = metrics_dict | calc_metrics(TP, TN, FP, FN, metric_prefix="micro_", metric_postfix="_default")

    return metrics_dict

def get_best_metrics_by_threshold(df):
    # calc metrics only if valid rows are present
    list_of_metrics = ["accuracy", "recall_incorrect", "recall_correct", "precision_incorrect", "precision_correct", "f1_incorrect", "f1_correct"]
    metrics_dict = {}
    # all thresholds metrics
    for metric in list_of_metrics:
        # Macro, collect FSN-level metrics and average across all FSNs
        metrics_dict["macro_%s" % metric] = np.asarray(df["%s_thresholds" % metric].to_list()).mean(axis=0)

    # Micro level metrics for different thresholds
    TP_ths, TN_ths, FP_ths, FN_ths = [
        np.asarray(df["%s_thresholds" % k].to_list()).sum(axis=0)
        for k in ["true_positive", "true_negative", "false_positive", "false_negative"]
    ]
    metrics_dict["TP"] = TP_ths
    metrics_dict["FP"] = FP_ths
    metrics_dict["TN"] = TN_ths
    metrics_dict["FN"] = FN_ths
    metrics_dict_ths = [
        calc_metrics(tp, tn, fp, fn, metric_prefix="micro_", metric_postfix="")
        for tp, tn, fp, fn in zip(TP_ths, TN_ths, FP_ths, FN_ths)
    ]
    merged_dict = defaultdict(list)
    for d in metrics_dict_ths:
        for key, value in d.items():
            merged_dict[key].append(value)
    metrics_dict = metrics_dict | dict(merged_dict)
    # diff between tnr and fnr taken from Ankit
    metrics_dict['tnr'] = metrics_dict['micro_recall_incorrect']
    metrics_dict['fnr'] = np.asarray(FN_ths) / (np.asarray(FN_ths) + np.asarray(TP_ths))
    metrics_dict['diff_tnr_fnr'] = (
        np.asarray(metrics_dict['tnr']) - np.asarray(metrics_dict['fnr'])
    )

    metrics_dict["threshold"] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    
    metrics_df = pd.DataFrame(metrics_dict)
    best_threshold = metrics_df.loc[metrics_df.diff_tnr_fnr.idxmax(), 'threshold']
    best_metrics_df = metrics_df[metrics_df['threshold'] == best_threshold]
    return best_metrics_df.to_dict("records")[0]

def calc_metrics(TP, TN, FP, FN, metric_prefix="", metric_postfix=""):
    metrics = {}
    metrics["%saccuracy%s" % (metric_prefix, metric_postfix)] = (TP + TN) / (TP + FN + TN + FP)

    recall_incorrect = TN / (TN + FP) if TN + FP != 0 else 1.0
    metrics["%srecall_incorrect%s" % (metric_prefix, metric_postfix)] = recall_incorrect 

    recall_correct = TP / (TP + FN) if TP + FN != 0 else 1.0
    metrics["%srecall_correct%s" % (metric_prefix, metric_postfix)] = recall_correct

    precision_incorrect = TN / (TN + FN) if TN + FN != 0 else 1.0
    metrics["%sprecision_incorrect%s" % (metric_prefix, metric_postfix)] = precision_incorrect

    precision_correct = TP / (TP + FP) if TP + FP != 0 else 1.0
    metrics["%sprecision_correct%s" % (metric_prefix, metric_postfix)] = precision_correct

    metrics["%sf1_incorrect%s" % (metric_prefix, metric_postfix)] = (
        0.0 if (precision_incorrect * recall_incorrect) == 0 else
        (2 * precision_incorrect * recall_incorrect) / (precision_incorrect + recall_incorrect)
    )
    metrics["%sf1_correct%s" % (metric_prefix, metric_postfix)] = (
        0.0 if (precision_correct * recall_correct) == 0 else
        (2 * precision_correct * recall_correct) / (precision_correct + recall_correct)
    )
    return metrics

def get_unique_tokens(keywords_str: str):
    keywords_str = re.sub('[^\w]+', ' ', keywords_str)
    keywords_list= keywords_str.split()
    unique_tokens = []
    for token in keywords_list:
        if not token in unique_tokens:
            unique_tokens.append(token)
    return unique_tokens

def calc_overlap_of_correct(true_tokens, pred_tokens):
    try:
        intersection = len(set(pred_tokens) & set(true_tokens))
        union = len(set(pred_tokens) | set(true_tokens))
        result = intersection/union
        return result
    except:
        return 0.0
