# PromptFlow Experimentation Framework

This experiment framework is a utility library that uses the prompt flow SDK to conduct, track and analyze experiments.

## Key Features of Experimentation Framework
* **Making the experiment execution process developer friendly** by providing apis based on promptflow sdk.
Framework offers APIs to create and run experiments, instead of using sdk functions directly.
* **Conduct experiments on local machines or on AML workspace Framework** can switch between local or AML workspace by modifying one input param. Data scientists can run experiments with small dataset on local machines and use AML workspace to run experiments with large datasets.
* **One-click execution of notebooks to run experiments with multiple flows and evaluation workflow**. Typically, the outputs of an experiment are fed as inputs to the evaluation stage. Data scientist may wish to run the evaluation stage following the experiment which may consists of multiple flows. In our case we had two step experiment followed by evaluation step. These stages can be merged into a notebook that can be executed with one click. This allows data scientists to run the entire workflow with minimal supervision.
* **Assigning unique ids as suffix** to identify multiple experiments from same notebook and **unique tags as prefix** to each run to track runs from multiple developers. This helps in monitoring of the experiments. 
* **Running experiments with multiple variants**. PromptFlow SDK api can create experiment runs with one variant at a time. To create runs with multiple variants, we have to use the sdk api repeatedly. Framework has simplified this process and allows data scientists to provide variant array as input and create multiple runs.
* **Run experiments with several connected runs**. PromptFlow SDK api can only make experiment runs with one connected run each time. To make runs with more than one connected run, we have to use the sdk api multiple times. Framework has eased this process and lets data scientists give a linked runs array as input and create many runs.
* **Get the outputs of the runs in either csv or jsonl format**. Framework provides utility functions to download the output of experiment and evaluation runs or merging outputs of multiple runs into one csv/jsonl file.
* **A custom python tool that leverages OpenAI to make requests**. It currently makes requests to the GPT4V model, but it can also be used for other Azure OpenAI models or our own models. Some of the features of the custom python tool are:  
    - Ability to send detailed param for running experiments for low and high resolution images.  
    - Ability to use multiple open ai connections in a round robin way for scaling up the experiment and reducing the time needed for completing the experiment.  
    - The custom python tool lets us include our own custom output params like prompt text, failure messages, temperature, top_k etc. that are hard to get from promptflow LLM tool

## Dev setup
Please follow [this link for the dev setup](./docs/dev-setup.md) details.

## Directory Structure
*   [docs](./docs/) : Contains the documentation.
*   [common](./common/): Contains common python files required for experiment execution
*   [keyword_correctness](./keyword_correctness/): Contains experiment and evaluation flow for keyword correctness use case. 

## DataScience Metrics
Datascience metrics used in the experimentation can be found [here.](./docs/data_science_metrics.md)

## Experiment Details
Please follow this [link](./docs/experiment_details.md) to get to know more about experiment details.

## Experiment Execution 
Please follow this [link](./docs/experiment_execution.md) to get to know more about experiment execution.



