# PromptFlow Experimentation Framework

This experiment framework is a utility library that uses the prompt flow SDK to conduct, track and analyze experiments.

## Key Features of Experimentation Framework

* **Developer-Friendly Experiment Execution**: Simplified APIs streamline the process of running experiments.

* **Flexible Execution Environment**: Experimentation can be conducted on both local machines and on Azure Machine Learning (AML) compute, facilitating seamless switching between environments based on dataset sizes.

* **Versatile Experiment Flows**: Enable the chaining of experiments, allowing easy passing of outputs from one experiment to another.

* **Efficient Experiment Tracking**: Unique identifiers and tags help monitor and differentiate experiments, aiding in efficient tracking and management.

* **Variants and Connected Runs**: Simplified APIs enable the creation of experiment runs with multiple variants and connected runs in a single step, this in turn will create multiple runs using PromptFlow automatically.

* **Output Management**: Provides utility functions to retrieve experiment outputs in various formats (CSV or JSONL) and merge outputs from multiple runs for streamlined analysis.

* **Custom Python Tool for GPT4 with Vision**: Offers a custom Python tool that allows to make GPT4 vision with `detail` [parameter to control the resolution](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/gpt-with-vision?tabs=rest%2Csystem-assigned%2Cresource#detail-parameter-settings-in-image-processing-low-high-auto).  Read more on the [implementation here](https://github.com/microsoft/dstoolkit-pf-exp-framework/blob/main/docs/gpt4v_tooling.md#openai-process-custom-python-tool).

## Dev setup

Please follow [this link for the dev setup](./docs/dev-setup.md) details.

### Directory Structure

* [docs](./docs/) : Contains the documentation.
* [common](./common/): Contains common python files required for experiment execution
* [keyword_correctness](./keyword_correctness/): Contains experiment and evaluation flow for keyword correctness use case. 

## Sample Experiment and Evaluation flows

Along with the framework, there is a sample use case for keyword correctness is implemented here with a two step experiment flows and also has an evaluation flow.

**Experiment architecture** - Read more on the [details of the experiment architecture](./docs/experiment_details.md)

**Guidelines to execute the experiments** - Follow this link to understand the [experiment execution](./docs/experiment_execution.md)

**Understand the metrics** - The sample evaluation flow evaluates the results, here is the breakdown of the metrics evaluated in the [evaluation flow](./docs/data_science_metrics.md)

### Walkthrough of Experimentation Framework

https://github.com/microsoft/dstoolkit-pf-exp-framework/assets/380340/e1bb878d-bf69-472b-b604-2eec5a18ed9d

