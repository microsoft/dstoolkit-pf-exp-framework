import pytest

from calculate_metrics import calculate_metrics, get_unique_tokens

# gt1 = {
#         "keyword1": "correct",
#         "keyword2": "correct",
#         "keyword3": "incorrect",
#         "keyword4": "incorrect",
#         "keyword5": "correct"
#     }
# pred1 = """[
#             {
#                 "keyword": "keyword1",
#                 "result": 0.8
#             },
#             {
#                 "keyword": "keyword2",
#                 "result": 0.9
#             },
#             {
#                 "keyword": "keyword3",
#                 "result": 0.4
#             },
#             {
#                 "keyword": "keyword4",
#                 "result": 0.0
#             },
#             {
#                 "keyword": "keyword5",
#                 "result": 0.4
#             }
#         ]"""

# gt2 = {
#         "keyword6": "correct",
#         "keyword7": "correct",
#         "keyword8": "incorrect",
#         "keyword9": "incorrect"
#     }
# pred2 = """[
#             {
#                 "keyword": "keyword6",
#                 "result": 0.8
#             },
#             {
#                 "keyword": "keyword7",
#                 "result": 0.9
#             },
#             {
#                 "keyword": "keyword8",
#                 "result": 0.4
#             },
#             {
#                 "keyword": "keyword9",
#                 "result": 0.0
#             }
#         ]"""

# gt3 = {
#         "keyword11": "correct",
#         "keyword12": "correct",
#         "keyword13": "incorrect",
#         "keyword14": "incorrect",
#         "keyword15": "correct"
#     }
# pred3 = """```json[
#             {
#                 "keyword": "keyword11",
#                 "result": 0.8
#             }
#         ]```"""


# gt4 = {
#     "keyword11": "correct",
#     "keyword12": "correct",
#     "keyword13": "incorrect",
#     "keyword14": "incorrect",
#     "keyword15": "correct"
# }
# pred4 = """[
#     {
#         "keywords": "keyword11",
#         "result": 0.8
#     },
#     {
#         "keyword": "keyword12",
#         "result": 0.9
#     },
#     {
#         "keyword": "keyword13",
#         "result": "correct 100"
#     },
#     {
#         "keyword": "keyword14",
#         "result": 0.0
#     },
#     {
#         "keyword": "keyword15",
#         "result": 0.4
#     }
# ]"""

grades = [{'keyword_count': 5, 'ground_truth': {'keyword1': 'correct', 'keyword2': 'correct', 'keyword3': 'incorrect', 'keyword4': 'incorrect', 'keyword5': 'correct'}, 'pred_big_parse_error': 0, 'pred_big_parse_error_msg': '', 'predictions': [{'keyword': 'keyword1', 'result': 0.8}, {'keyword': 'keyword2', 'result': 0.9}, {'keyword': 'keyword3', 'result': 0.4}, {'keyword': 'keyword4', 'result': 0.0}, {'keyword': 'keyword5', 'result': 0.4}], 'pred_small_parse_errors': [(True, 'OK'), (True, 'OK'), (True, 'OK'), (True, 'OK'), (True, 'OK')], 'pred_small_parse_errors_count': 0, 'recall_correct': 0.6666666666666666, 'recall_incorrect': 1.0, 'precision_correct': 1.0, 'precision_incorrect': 0.6666666666666666, 'f1_correct': 0.8, 'f1_incorrect': 0.8, 'accuracy': 0.8, 'true_negative': 2, 'true_positive': 2, 'false_negative': 1, 'false_positive': 0, 'recall_correct_thresholds': (1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.3333333333333333, 0.0), 'recall_incorrect_thresholds': (0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), 'precision_correct_thresholds': (0.75, 0.75, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0), 'precision_incorrect_thresholds': (1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.5, 0.4), 'f1_correct_thresholds': (0.8571428571428571, 0.8571428571428571, 0.8571428571428571, 0.8571428571428571, 0.8, 0.8, 0.8, 0.8, 0.5, 0.0), 'f1_incorrect_thresholds': (0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.8, 0.8, 0.8, 0.8, 0.6666666666666666, 0.5714285714285715), 'accuracy_thresholds': (0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.6, 0.4), 'true_negative_thresholds': (1, 1, 1, 1, 2, 2, 2, 2, 2, 2), 'true_positive_thresholds': (3, 3, 3, 3, 2, 2, 2, 2, 1, 0), 'false_negative_thresholds': (0, 0, 0, 0, 1, 1, 1, 1, 2, 3), 'false_positive_thresholds': (1, 1, 1, 1, 0, 0, 0, 0, 0, 0)}, {'keyword_count': 4, 'ground_truth': {'keyword6': 'correct', 'keyword7': 'correct', 'keyword8': 'incorrect', 'keyword9': 'incorrect'}, 'pred_big_parse_error': 0, 'pred_big_parse_error_msg': '', 'predictions': [{'keyword': 'keyword6', 'result': 0.8}, {'keyword': 'keyword7', 'result': 0.9}, {'keyword': 'keyword8', 'result': 0.4}, {'keyword': 'keyword9', 'result': 0.0}], 'pred_small_parse_errors': [(True, 'OK'), (True, 'OK'), (True, 'OK'), (True, 'OK')], 'pred_small_parse_errors_count': 0, 'recall_correct': 1.0, 'recall_incorrect': 1.0, 'precision_correct': 1.0, 'precision_incorrect': 1.0, 'f1_correct': 1.0, 'f1_incorrect': 1.0, 'accuracy': 1.0, 'true_negative': 2, 'true_positive': 2, 'false_negative': 0, 'false_positive': 0, 'recall_correct_thresholds': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5, 0.0), 'recall_incorrect_thresholds': (0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0), 'precision_correct_thresholds': (0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0), 'precision_incorrect_thresholds': (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.5), 'f1_correct_thresholds': (0.8, 0.8, 0.8, 0.8, 1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.0), 'f1_incorrect_thresholds': (0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 1.0, 1.0, 1.0, 1.0, 0.8, 0.6666666666666666), 'accuracy_thresholds': (0.75, 0.75, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 0.75, 0.5), 'true_negative_thresholds': (1, 1, 1, 1, 2, 2, 2, 2, 2, 2), 'true_positive_thresholds': (2, 2, 2, 2, 2, 2, 2, 2, 1, 0), 'false_negative_thresholds': (0, 0, 0, 0, 0, 0, 0, 0, 1, 2), 'false_positive_thresholds': (1, 1, 1, 1, 0, 0, 0, 0, 0, 0)}, {'keyword_count': 5, 'ground_truth': {'keyword11': 'correct', 'keyword12': 'correct', 'keyword13': 'incorrect', 'keyword14': 'incorrect', 'keyword15': 'correct'}, 'pred_big_parse_error': 1, 'pred_big_parse_error_msg': 'Error parsing predictions as json', 'predictions': [], 'pred_small_parse_errors': [], 'pred_small_parse_errors_count': 0}, {'keyword_count': 5, 'ground_truth': {'keyword11': 'correct', 'keyword12': 'correct', 'keyword13': 'incorrect', 'keyword14': 'incorrect', 'keyword15': 'correct'}, 'pred_big_parse_error': 0, 'pred_big_parse_error_msg': '', 'predictions': [{'keywords': 'keyword11', 'result': 0.8}, {'keyword': 'keyword12', 'result': 0.9}, {'keyword': 'keyword13', 'result': 'correct 100'}, {'keyword': 'keyword14', 'result': 0.0}, {'keyword': 'keyword15', 'result': 0.4}], 'pred_small_parse_errors': [(False, 'Required keys not present in prediction dict'), (True, 'OK'), (False, 'Predicted value not in valid range for str'), (True, 'OK'), (True, 'OK')], 'pred_small_parse_errors_count': 2}]
expected_metrics = {
    "pred_big_parse_errors_count": 1,
    "pred_big_parse_errors_ratio": 1/4,
    "fsn_pred_small_parse_errors_count": 1,
    "fsn_pred_small_parse_errors_ratio": 1/4,
    "total_pred_small_parse_errors_count": 2,
    "total_pred_small_parse_errors_ratio": 2/19,
    # macro/fsn level metrics
    'macro_accuracy': 0.9,
    'macro_recall_incorrect': 1.0,
    'macro_recall_correct': 0.8333333333333333,
    'macro_precision_incorrect': 0.8333333333333333,
    'macro_precision_correct': 1.0,
    'macro_f1_incorrect': 0.9,
    'macro_f1_correct': 0.9,
    # micro/total level metrics
    'micro_accuracy': 0.8888888888888888,
    'micro_recall_incorrect': 1.0,
    'micro_recall_correct': 0.8,
    'micro_precision_incorrect': 0.8,
    'micro_precision_correct': 1.0,
    'micro_f1_incorrect': 0.888888888888889,
    'micro_f1_correct': 0.888888888888889
}

def _assert_metrics(result, expected_metrics_dict):
    assert type(result) is dict
    for k, v in expected_metrics_dict.items():
        assert k in expected_metrics_dict.keys()
        assert result[k] == v
    # TODO: check if all the expected metrics are present and in correct format

def test_calculate_metrics():
    result = calculate_metrics(
        grades
    )
    _assert_metrics(result, expected_metrics)

def test_get_unique_tokens():
    io_tuples = [
        ("virat RCB jersey,rcb jersey virat kohli,virat kohli rcb jersey", ["RCB", "rcb", "virat", "jersey", "kohli"]),
        ("1,:2 '3 '4 |5-6 (7) 8 9", ["1", "2", "3", "4", "5", "6", "7"])
    ]
    for row in io_tuples:
        assert set(get_unique_tokens(row[0])[:7]) == set(row[1])
