import pytest

from grade import grade


class TestCorrect:
    gt = {
        "keyword1": "correct",
        "keyword2": "correct",
        "keyword3": "incorrect",
        "keyword4": "incorrect",
        "keyword5": "correct"
    }
    expected_metrics_dict = {
        "recall_correct": 2/3,
        "recall_incorrect": 1.0,
        "precision_correct": 1.0,
        "precision_incorrect": 2/3,
        "f1_correct": 0.8,
        "f1_incorrect": 0.8,
        "accuracy": 0.8,
    }
    expected_thresholded_metrics_dict = {
        'recall_correct_thresholds': (1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.3333333333333333, 0.0),
        'recall_incorrect_thresholds': (0.5, 0.5, 0.5, 0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        'precision_correct_thresholds': (0.75, 0.75, 0.75, 0.75, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0),
        'precision_incorrect_thresholds': (1.0, 1.0, 1.0, 1.0, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.5, 0.4),
        'f1_correct_thresholds': (0.8571428571428571, 0.8571428571428571, 0.8571428571428571, 0.8571428571428571, 0.8, 0.8, 0.8, 0.8, 0.5, 0.0),
        'f1_incorrect_thresholds': (0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.6666666666666666, 0.8, 0.8, 0.8, 0.8, 0.6666666666666666, 0.5714285714285715),
        'accuracy_thresholds': (0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.6, 0.4),
        'true_negative_thresholds': (1, 1, 1, 1, 2, 2, 2, 2, 2, 2),
        'true_positive_thresholds': (3, 3, 3, 3, 2, 2, 2, 2, 1, 0),
        'false_negative_thresholds': (0, 0, 0, 0, 1, 1, 1, 1, 2, 3),
        'false_positive_thresholds': (1, 1, 1, 1, 0, 0, 0, 0, 0, 0)
    }

    def _assert_metrics(self, result, expected_metrics_dict):
        assert type(result) is dict
        for k, v in expected_metrics_dict.items():
            assert k in result.keys()
            assert result[k] == v
        # TODO: check if all the expected metrics are present and in correct format

    def test_markdown_json(self):
        pred = """```json
        [
            {
                "keyword": "keyword1",
                "result": 0.8
            },
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            },
            {
                "keyword": "keyword5",
                "result": 0.4
            }
        ]
        ```"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_metrics_dict)


    def test_single_keyword(self):
        gt = {
            "keyword1": "incorrect"
        }
        pred = """[
            {
                "keyword": "keyword1",
                "result": "incorrect"
            }
        ]"""
        metrics = {
            "recall_correct": 1.0,
            "recall_incorrect": 1.0,
            "precision_correct": 1.0,
            "precision_incorrect": 1.0,
            "f1_correct": 1.0,
            "f1_incorrect": 1.0,
            "accuracy": 1.0,
        }
        result = grade(
            gt,
            pred
        )
        self._assert_metrics(result, metrics)

        gt = {
            "keyword1": "correct"
        }
        pred = """[
            {
                "keyword": "keyword1",
                "result": "correct"
            }
        ]"""
        metrics = {
            "recall_correct": 1.0,
            "recall_incorrect": 1.0,
            "precision_correct": 1.0,
            "precision_incorrect": 1.0,
            "f1_correct": 1.0,
            "f1_incorrect": 1.0,
            "accuracy": 1.0,
        }
        result = grade(
            gt,
            pred
        )
        self._assert_metrics(result, metrics)

        gt = {
            "keyword1": "correct"
        }
        pred = """[
            {
                "keyword": "keyword1",
                "result": "incorrect"
            }
        ]"""
        metrics = {
            "recall_correct": 0.0,
            "recall_incorrect": 1.0,
            "precision_correct": 1.0,
            "precision_incorrect": 0.0,
            "f1_correct": 0.0,
            "f1_incorrect": 0.0,
            "accuracy": 0.0,
        }
        result = grade(
            gt,
            pred
        )
        self._assert_metrics(result, metrics)
        
        gt = {
            "keyword1": "incorrect"
        }
        pred = """[
            {
                "keyword": "keyword1",
                "result": "correct"
            }
        ]"""
        metrics = {
            "recall_correct": 1.0,
            "recall_incorrect": 0.0,
            "precision_correct": 0.0,
            "precision_incorrect": 1.0,
            "f1_correct": 0.0,
            "f1_incorrect": 0.0,
            "accuracy": 0.0,
        }
        result = grade(
            gt,
            pred
        )
        self._assert_metrics(result, metrics)

    def test_thresholded_metrics(self):
        pred = """[
            {
                "keyword": "keyword1",
                "result": 0.8
            },
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            },
            {
                "keyword": "keyword5",
                "result": 0.4
            }
        ]"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_thresholded_metrics_dict)

    def test_float(self):
        pred = """[
            {
                "keyword": "keyword1",
                "result": 0.8
            },
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            },
            {
                "keyword": "keyword5",
                "result": 0.4
            }
        ]"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_metrics_dict)

    def test_string(self):
        pred = """[
            {
                "keyword": "keyword1",
                "result": "correct"
            },
            {
                "keyword": "keyword2",
                "result": "correct"
            },
            {
                "keyword": "keyword3",
                "result": "incorrect"
            },
            {
                "keyword": "keyword4",
                "result": "incorrect"
            },
            {
                "keyword": "keyword5",
                "result": "incorrect"
            }
        ]"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_metrics_dict)

    def test_int(self):
        pred = """[
            {
                "keyword": "keyword1",
                "result": 8
            },
            {
                "keyword": "keyword2",
                "result": 9
            },
            {
                "keyword": "keyword3",
                "result": 4
            },
            {
                "keyword": "keyword4",
                "result": 0
            },
            {
                "keyword": "keyword5",
                "result": 4
            }
        ]"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_metrics_dict)

    def test_bool(self):
        pred = """[
            {
                "keyword": "keyword1",
                "result": true
            },
            {
                "keyword": "keyword2",
                "result": true
            },
            {
                "keyword": "keyword3",
                "result": false
            },
            {
                "keyword": "keyword4",
                "result": false
            },
            {
                "keyword": "keyword5",
                "result": false
            }
        ]"""
        result = grade(
            self.gt,
            pred
        )
        self._assert_metrics(result, self.expected_metrics_dict)


class TestFaulty:
    correct_gt = {
        "keyword1": "correct",
        "keyword2": "correct",
        "keyword3": "incorrect",
        "keyword4": "incorrect",
        "keyword5": "correct"
    }
    correct_pred = """[
        {
            "keyword": "keyword1",
            "result": 0.8
        },
        {
            "keyword": "keyword2",
            "result": 0.9
        },
        {
            "keyword": "keyword3",
            "result": 0.4
        },
        {
            "keyword": "keyword4",
            "result": 0.0
        },
        {
            "keyword": "keyword5",
            "result": 0.4
        }
    ]"""
    
    def test_keywords_count(self):
        pred = """[
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            }
        ]"""
        result = grade(
            self.correct_gt,
            pred
        )
        assert result["pred_big_parse_error"] == 1
        assert result["pred_big_parse_error_msg"] == "Predictions not a list or # of keywords in predictions is different than # of GT keywords."

    def test_keywords_mismatch(self):
        pred = """[
            {
                "keyword": "keyword5",
                "result": 0.4
            },
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            },
            {
                "keyword": "keyword1",
                "result": 0.8
            }
        ]"""
        result = grade(
            self.correct_gt,
            pred
        )
        print(result)
        assert result["pred_big_parse_error"] == 1
        assert result["pred_big_parse_error_msg"] == "Predictions keywords different than GT keywords"

    def test_json_parsing(self):
        pred = """
        [
            {
                "keyword": "keyword5",
                "result": 0.4,
                "assagas"
            },
            {
                "keyword": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "result": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 0.0
            },
            {
                "keyword": "keyword1",
                "result": 0.8
            }
        ]
        """
        result = grade(
            self.correct_gt,
            pred
        )
        print(result)
        assert result["pred_big_parse_error"] == 1
        assert result["pred_big_parse_error_msg"] == "Error parsing predictions as json"
        
    def test_small_parse_error(self):
        pred = """
        [
            {
                "keyword": "keyword1",
                "result": 0.8
            },
            {
                "incorrect_key": "keyword2",
                "result": 0.9
            },
            {
                "keyword": "keyword3",
                "incorrect_key": 0.4
            },
            {
                "keyword": "keyword4",
                "result": 100
            },
            {
                "keyword": "keyword5",
                "result": "incorrect label"
            }
        ]
        """
        result = grade(
            self.correct_gt,
            pred
        )
        print(result)
        assert result["pred_small_parse_errors_count"] == 4
        assert result["pred_small_parse_errors"] == [
            (True, "OK"),
            (False, "Required keys not present in prediction dict"),
            (False, "Required keys not present in prediction dict"),
            (False, "Predicted value not in valid range for int"),
            (False, "Predicted value not in valid range for str")
        ]
