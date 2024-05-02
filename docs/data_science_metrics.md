### Metrics we currently capture in evaluation flow

#### Macro-Avereged DS Metrics:
Metrics calculated separately on each FSN level and then aggregated and averaged across all FSNs.

| **metric name** | **description** |
| --- | --- |
| macro_recall_incorrect | FSN-level [recall](https://en.wikipedia.org/wiki/Precision_and_recall) of incorrect keywords avereged across all FSNs. Primary metric we measure our performance against|
| macro_recall_correct | Same as above but from correct keywords POV |
| macro_precision_incorrect | FSN-level [precision](https://en.wikipedia.org/wiki/Precision_and_recall) of incorrect keywords avereged across all FSNs. Secondary metric to give us a better view of mislclassifications |
| macro_precision_correct | Same as above but from correct keywords POV |
| macro_accuracy | General [accuracy](https://en.wikipedia.org/wiki/Accuracy_and_precision#In_binary_classification) metric. |
| macro_f1_incorrect | [F1 Score](https://en.wikipedia.org/wiki/F-score) of incorrect keywords |
| macro_f1_correct | Same as above but for correct keywords |

#### Micro-Avereged DS Metrics:
Individual keyword level results aggregated and metrics calculated on total set of keywords.

| **metric name** | **description** |
| --- | --- |
| micro_recall_incorrect | [Recall](https://en.wikipedia.org/wiki/Precision_and_recall) of incorrect keywords calculated on aggregated predictions for all keywords|
| micro_recall_correct | Same as above but from correct keywords POV |
| micro_precision_incorrect | [Precision](https://en.wikipedia.org/wiki/Precision_and_recall) of incorrect keywords calculated from all keywords predictions |
| micro_precision_correct | Same as above but from correct keywords POV |
| micro_accuracy | General [accuracy](https://en.wikipedia.org/wiki/Accuracy_and_precision#In_binary_classification) metric |
| micro_f1_incorrect | [F1 Score](https://en.wikipedia.org/wiki/F-score) of incorrect keywords |
| micro_f1_correct | Same as above but for correct keywords |

#### Error rate metrics:

| **metric name** | **description** |
| --- | --- |
| pred_big_parse_errors_count | Count of BIG parsing errors. Rows with these errors don't participate in DS metrics calculation  |
| pred_big_parse_errors_ratio | Same as above but expressed in ratio: `errors count / total number of FSNs in dataset` |
| fsn_pred_small_parse_errors_count | Count of SMALL parsing errors where one or more predictions in the list failed the validation/parsing step. Rows with these errors don't participate in DS metrics calculation  |
| fsn_pred_small_parse_errors_ratio | Same as above but expressed in ratio: `number of FSNs were these errors occured / total number of FSNs in dataset` |
| total_pred_small_parse_errors_count | Total count of SMALL parsing errors. Each error represent a problem with formatting of a single keyword prediction |
| total_pred_small_parse_errors_ratio | Ratio of total count of SMALL parsing errors vs total number of keywords in the dataset |
