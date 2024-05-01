from io import StringIO
import re
import pandas as pd
from promptflow import tool
import json
import numpy as np
import logging
from typing import List
from calculate_metrics import calc_metrics


logger = logging.getLogger(__name__)


@tool
def grade(ground_truth: dict, predictions_str: str):
    """
    Grade the predictions based on the ground truth and calculate metrics.

    Args:
        ground_truth (dict): A dictionary containing the ground truth keywords and their labels.
        predictions_str (str): A string containing the predictions in JSON or CSV format.

    Returns:
        dict: A dictionary containing the grading results and calculated metrics.
    """
    output_dict = get_default_output_dict()
    # get keywords count from ground truth dict
    keyword_count = len(ground_truth.keys())
    output_dict["keyword_count"] = keyword_count
    output_dict["ground_truth"] = ground_truth

    # try parse output prediction coming from llm
    try:
        predictions = parse_predictions(predictions_str)
        output_dict["predictions"] = predictions
    except:
        # stop processing and return output_dict in case of issues
        output_dict["predictions"] = predictions_str
        output_dict["pred_big_parse_error"] = 1
        output_dict["pred_big_parse_error_msg"] = "Error parsing predictions as json"
        return output_dict

    # if json is a dict means we most likely have a single keyword prediction so we need to put it in a list
    if type(predictions) is dict:
        predictions = [predictions]
        output_dict["predictions"] = predictions

    # cases for which stop processing
    if type(predictions) is not list or keyword_count != len(predictions):
        output_dict["pred_big_parse_error"] = 1
        output_dict["pred_big_parse_error_msg"] = "Predictions not a list or # of keywords in predictions is different than # of GT keywords."
        return output_dict

    # iterate through all predictions and validate format, types and ranges
    # validation result is a tuple of bool (valid or not) and str (error message) for each keyword
    # example validation_results: [(True, "OK"), (False, "Predicted value not in valid types")]
    validation_results = [validate_prediction(pred) for pred in predictions]
    output_dict["pred_small_parse_errors"] = validation_results
    # split validation results pairs into separate lists and log number of errors
    validation_bools, _ = zip(*validation_results)
    output_dict["pred_small_parse_errors_count"] = validation_bools.count(
        False)
    # in case of any errors, finish processing
    # TODO: Should we continue processing predictions?
    if output_dict["pred_small_parse_errors_count"] > 0:
        return output_dict

    # in ground_truth, strip consecutive spaces between words and remove leading/trailing spaces
    gt = {}
    rank_gt = {}
    for i, k in enumerate(ground_truth):
        new_k = re.sub(r"\s+", " ", str(k)).strip() if k is not None else ""
        gt[new_k] = ground_truth[k]
        rank_gt[new_k] = i
    ground_truth = gt

    # in predictions, strip consecutive spaces between words and remove leading/trailing spaces
    for p in predictions:
        p["keyword"] = re.sub(r"\s+", " ", str(p["keyword"])
                              ).strip() if p["keyword"] is not None else ""
        
    # sort the predictions on keywords based on rank in rank_gt
    predictions = sorted(predictions, key=lambda x: rank_gt.get(x["keyword"], float('inf')))

    # validate if ground truth and predictions keywords are the same:
    gt_keywords = list(ground_truth.keys())
    pred_keywords = [p["keyword"] for p in predictions]
    if gt_keywords != pred_keywords:
        diff_kw = []
        for kw1, kw2 in zip(gt_keywords, pred_keywords):
            if kw1 != kw2: diff_kw.append([kw1, kw2])
        output_dict["pred_big_parse_error"] = 1
        output_dict["pred_big_parse_error_msg"] = "Predictions keywords different than GT keywords"
        output_dict["different_keywords"] = diff_kw
        return output_dict

    # METRICS CALCULATION
    # ensure y_true and y_pred are float values
    y_true = convert_labels_to_float(ground_truth.values())
    y_pred = [p["result"] for p in predictions]
    y_pred = convert_labels_to_float(y_pred)
    for p, v in zip(predictions, y_pred):
        p["result"] = v
    output_dict["predictions"] = predictions

    # calculate metrics for default threshold
    metrics_dict = get_metrics(y_true, y_pred, conf_threshold=0.8, metric_postfix="")
    # add metrics to output
    output_dict = output_dict | metrics_dict

    # calculate metrics for range of confidence thresholds
    metrics_thresholded_list = []
    for conf_threshold in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        # we calculate metrics for each threshold separately and append to a list
        metrics_thresholded_list.append(get_metrics(
            y_true, y_pred, conf_threshold=conf_threshold, metric_postfix="_thresholds"))
    # we gather metrics for all thresholds and create a single dictionary with values of list type
    keys = metrics_thresholded_list[0].keys()
    values = zip(*[d.values() for d in metrics_thresholded_list])
    # final metrics look like this: { "accuracy": [0.5, 0.6, 0.7, 0.8, 0.8, 0.85, 0.87, 0.89, 0.90. 0.95] }
    metrics_thresholded_dict = dict(zip(keys, values))
    # add thresholded metrics to output_dict
    output_dict = output_dict | metrics_thresholded_dict
    return output_dict


def parse_predictions(predictions_str):
    """
    Parses the predictions string and returns a list of prediction records.

    Args:
        predictions_str (str): The string containing predictions in either JSON or CSV format.

    Returns:
        list: A list of prediction records. Each record is a dictionary with 'keyword', 'reason', and 'result' keys.

    Raises:
        ValueError: If the predictions string is not in a valid JSON or CSV format.
    """
    # detect if predictions_str is array of json or csv
    predictions_str = predictions_str.replace(
        "```json", "").replace("```csv", "").replace("```", "")
    if predictions_str.startswith("[") or predictions_str.startswith("{"):
        predictions = json.loads(predictions_str)
    else:
        predictions = pd.read_csv(StringIO(predictions_str), sep="\s*\|\s*", header=None, quotechar="'", skipinitialspace=True, quoting=1, names=[
                                  'keyword', 'reason', 'result'], dtype={'result': np.int32}, engine='python')
        predictions['keyword'] = predictions['keyword'].str.replace(
            "^'|'$", '', regex=True)
        predictions['keyword'] = predictions['keyword'].str.replace(
            '^"|"$', '', regex=True)
        predictions = predictions.to_dict(orient='records')
    return predictions



def get_metrics(y_true, y_pred, conf_threshold, metric_postfix):
    """
    Calculate evaluation metrics based on true labels and predicted labels.

    Args:
        y_true (array-like): True labels.
        y_pred (array-like): Predicted labels.
        conf_threshold (float): Confidence threshold for binary classification.
        metric_postfix (str): Postfix to append to metric names.

    Returns:
        dict: A dictionary containing the evaluation metrics.

    """
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    # apply confidence threshold
    y_pred[y_pred >= conf_threshold] = 1.0
    y_pred[y_pred < conf_threshold] = 0.0

    # get tn, tp, fn, fp
    TP, TN, FP, FN = (
        sum((y_true == 1) * (y_pred == 1)),
        sum((y_true == 0) * (y_pred == 0)),
        sum((y_pred == 1) * (y_pred != y_true)),
        sum((y_pred == 0) * (y_pred != y_true))
    )

    metrics_dict = {
        "true_negative%s" % metric_postfix: TN,
        "true_positive%s" % metric_postfix: TP,
        "false_negative%s" % metric_postfix: FN,
        "false_positive%s" % metric_postfix: FP,
        "gt_vs_pred%s" % metric_postfix: list(np.asarray(y_true == y_pred, dtype=float))
    }
    metrics_dict = metrics_dict | calc_metrics(
        TP, TN, FP, FN, metric_postfix=metric_postfix)
    for k, v in metrics_dict.items():
        if type(v) != list:
            metrics_dict[k] = float(v)
    return metrics_dict


def get_default_output_dict():
    """
    Returns a default output dictionary with the following keys and initial values:
    
    - "keyword_count": 0, count of keywords in ground truth
    - "ground_truth": {}, ground truth dictionary
    - "pred_big_parse_error": 0, error parsing predictions as json
    - "pred_big_parse_error_msg": "", error parsing predictions as json
    - "predictions": [], list of predictions
    - "pred_small_parse_errors": [], list of formatting errors in predictions + reason
    - "pred_small_parse_errors_count": 0, number of formatting errors predictions
    
    Returns:
        dict: A default output dictionary.
    """
    output_dict = {
        "keyword_count": 0,
        "ground_truth": {},
        "pred_big_parse_error": 0,
        "pred_big_parse_error_msg": "",
        "predictions": [],
        "pred_small_parse_errors": [],
        "pred_small_parse_errors_count": 0,
    }
    return output_dict


def convert_labels_to_float(labels_list: List):
    """
    Converts a list of labels to a list of floats.

    Args:
        labels_list (List): A list of values representing labels.

    Returns:
        List: A list of floats representing the converted labels.
    """
    new_labels = []
    for label in labels_list:
        if type(label) is str:
            new_labels.append(1.0 if label == "correct" else 0.0)
        elif type(label) is bool:
            new_labels.append(float(label))
        elif type(label) is int:
            new_labels.append(label/10)
        elif type(label) is float:
            new_labels.append(label)
    return new_labels


def validate_prediction(prediction: dict):
    '''
    Expected input:
    prediction = {
        "keyword": "keyword1",
        "result": "correct" | 9 | 0.9 | True
    }

    Outputs:
    (True/False, error_message)
    '''
    try:
        # check if required keys are present in the prediction dict
        required_k = ["keyword", "result"]
        assert all([k in prediction.keys() for k in required_k]
                   ), "Required keys not present in prediction dict"
        # check `result`` values are of correct type and range
        valid_v_types = [int, float, str, bool]
        v = prediction['result']
        assert type(v) in valid_v_types, "Predicted value not in valid types"
        if type(v) is float:
            assert v >= 0.0 and v <= 1.0, "Predicted value not in valid range for float"
        elif type(v) is int:
            assert v >= 0 and v <= 10, "Predicted value not in valid range for int"
        elif type(v) is str:
            assert v in [
                "correct", "incorrect"], "Predicted value not in valid range for str"
        else:
            assert v in [
                True, False], "Predicted value not in valid range for bool"
    except Exception as e:
        # if assertion fails, return False + Error message
        return (False, str(e))
    # if all good, return True and "OK"
    return (True, "OK")
