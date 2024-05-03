from entities import Flow


experiment_step1_column_mapping = {
    "row_index": "${data.row_index}",
    "fsn": "${data.fsn}",
    "images": "${data.images}",
    "grounding_attributes": "${data.grounding_attributes}",
    "keywords": "${data.keywords}"
}

experiment_step1_flow = Flow(
    "experiment_step1",
    "This is first part of experiment, involving only GPT4 with vision and converts image to text",
    "../keyword_correctness/flows/experiment_step1/",
    experiment_step1_column_mapping,
    ["${openai_process.variant_0}","${openai_process.variant_1}"]
)

experiment_step2_column_mapping = {
    "fsn": "${data.fsn}",
    "grounding_attributes": "${data.grounding_attributes}",
    "description_from_llm": "${data.description_from_llm}",
    "keywords": "${data.ground_truth}"
}

experiment_step2_flow = Flow(
    "experiment_step2",
    "This is the second part of the experiment, here the data from the first part is used along with GPT 3.5 Turbo",
    "../keyword_correctness/flows/experiment_step2/",
    experiment_step2_column_mapping,
    ["${llm_prompt.variant_0}","${llm_prompt.variant_1}","${llm_prompt.variant_2}"]
)

evaluation_column_mapping = {
    "fsn": "${data.fsn}",
    "ground_truth": "${data.ground_truth}",
    "predictions_str": "${data.experiment_result}"
}

evaluation_flow = Flow(
    "evaluation",
    "This is the evaluation flow, where the predictions are evaluated",
    "../keyword_correctness/flows/evaluation/",
    evaluation_column_mapping,
    []
)


