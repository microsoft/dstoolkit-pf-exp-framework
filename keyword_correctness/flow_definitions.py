from entities import Flow

experiment_1_column_mapping = {
    "fsn": "${data.fsn}",
    "images": "${data.images}",
    "grounding_attributes": "${data.grounding_attributes}",
    "keywords": "${data.keywords}"
}

experiment_1_flow = Flow(
    "experiment_1",
    "This is experiment 1, involving only GPT4 with vision model",
    "../keyword_correctness/flows/experiment_1/",
    experiment_1_column_mapping,
    []
)

# override default values for seed, temperature, top_p, max_tokens, resolution
experiment_2_column_mapping = {
    "row_index": "${data.row_index}",
    "fsn": "${data.fsn}",
    "images": "${data.images}",
    "grounding_attributes": "${data.grounding_attributes}",
    "keywords": "${data.keywords}",
    "seed": 13,
    "temperature": 0.0,
    "top_p": 0.1,
    "max_tokens": 2500,
    "resolution": "low"
}

experiment_2_flow = Flow(
    "experiment_2",
    "This is experiment 2, involving only GPT4 with vision model",
    "../keyword_correctness/flows/experiment_2/",
    experiment_2_column_mapping,
    []
)

experiment_3_column_mapping = {
    "fsn": "${data.fsn}",
    "keywords": "${data.keywords}",
    "grounding_attributes": "${data.grounding_attributes}",
}

experiment_3_flow = Flow(
    "experiment_3",
    "This is experiment 3, involving only GPT3.5 Turbo and text input",
    "../keyword_correctness/flows/experiment_3_gpt3.5/",
    experiment_3_column_mapping,
    ["${llm_prompt.variant_0}", "${llm_prompt.variant_1}", "${llm_prompt.variant_2}", "${llm_prompt.variant_3}",
        "${llm_prompt.variant_4}", "${llm_prompt.variant_5}", "${llm_prompt.variant_6}", "${llm_prompt.variant_7}"]
)

experiment_4_1_column_mapping = {
    "row_index": "${data.row_index}",
    "fsn": "${data.fsn}",
    "images": "${data.images}",
    "grounding_attributes": "${data.grounding_attributes}",
    "keywords": "${data.keywords}"
}

experiment_4_1_flow = Flow(
    "experiment_4_1",
    "This is first part of experiment 4, involving only GPT4 with vision and converts image to text",
    "../keyword_correctness/flows/experiment_4_1/",
    experiment_4_1_column_mapping,
    ["${image_to_results_lmm.variant_0}"]
)

experiment_4_2_column_mapping = {
    "fsn": "${data.fsn}",
    "grounding_attributes": "${data.grounding_attributes}",
    "description_from_llm": "${data.description_from_llm}",
    "keywords": "${data.ground_truth}"
}

experiment_4_2_flow = Flow(
    "experiment_4_2",
    "This is the second part of the experiment 4, here the data from the first part is used along with GPT 3.5 Turbo",
    "../keyword_correctness/flows/experiment_4_2/",
    experiment_4_2_column_mapping,
    ["${validate_keywords.variant_0}"]
)

evaluation_column_mapping = {
    # "fsn": "${run.outputs.fsn}",
    # "grounding_attributes": "${run.outputs.grounding_attributes}",
    # "ground_truth": "${run.outputs.ground_truth}",
    # "predictions_str": "${run.outputs.experiment_result}"
    "fsn": "${data.fsn}",
    # "grounding_attributes": "${data.grounding_attributes}",
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

comparative_analysis_column_mapping = {
    # "fsn": "${run.outputs.fsn}",
    # "grounding_attributes": "${run.outputs.grounding_attributes}",
    # "ground_truth": "${run.outputs.ground_truth}",
    # "predictions_str": "${run.outputs.experiment_result}"
    "experiment1": "${data.experiment1}",
    # "grounding_attributes": "${data.grounding_attributes}",
    "experiment2": "${data.experiment2}",
    "effect_size": 0.5,
    "alpha": 0.05,
    "power": 0.8
}

comparative_analysis = Flow(
    "comparative_analysis",
    "This is the flow to perform comparative analysis between two experiments",
    "../keyword_correctness/flows/comparative_analysis/",
    comparative_analysis_column_mapping,
    []
)
