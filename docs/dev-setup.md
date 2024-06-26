# Dev environment setup

## Prerequisites

- [VS Code](https://code.visualstudio.com/download)
- [AZ CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
- [Python version 3.11.9](https://www.python.org/downloads/release/python-3119/)

## Virtual Environment Setup

- Install `make` utility if not already installed.
  - For [Windows](https://community.chocolatey.org/packages/make), you can use `choco` to install `make` using `choco install make` command.
  - For [Mac](https://formulae.brew.sh/formula/make), you can use `brew` to install `make` using `brew install make` command.
- Run `make install` to setup a Python virtual environment and install the necessary packages.

## Create following resources in Azure

- Create an Azure Machine Learning Workspace on Azure portal.
- The example in this repo uses GPT4 with vision-preview and GPT3.5 turbo models. 
  -  Create Azure OpenAI instances in regions where gpt-4, vision preview is available. We can check availability from this [link.](https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/models#gpt-4-and-gpt-4-turbo-preview-model-availability)
  - Deploy GPT4 models with model version vision-preview. Please use `gpt-4v` as deployment name
  -  Deploy GPT3.5 Turbo model. Please use `gpt-35` as deployment name
- Create an [Azure Machine Learning compute instance](https://learn.microsoft.com/en-us/azure/machine-learning/how-to-create-compute-instance?view=azureml-api-2&tabs=azure-studio) on the Azure portal. For development purposes, you can select the `Standard_DS11_v2` CPU instance type.
- Create a [prompt flow compute instance runtime](https://learn.microsoft.com/en-us/azure/machine-learning/prompt-flow/how-to-create-manage-runtime?view=azureml-api-2&tabs=cli%2Cpython#create-a-compute-instance-runtime-on-a-runtime-page) by selecting the compute instance created in the previous step.

> Note: Idle shutdown does not occur on the AML computes which have prompt flow runtimes installed on them. Hence, please ensure to shutdown your compute instances when not in use.  

> *Note: Recently new [`GPT4o` model](https://openai.com/index/hello-gpt-4o/) is launched. This model also supports images. Instead of GPT4v we can also use GPT4o model. Please follow similare steps to create connection and update flow.dag.yaml file to use GPT4o model.*

## Setup `.env` file

Copy the `.env-template` file as `.env` and update the values.

## Login to Azure

- Make sure to login to Azure using `az login` command
- Set default values for Azure

```cli
az account set --subscription <my-sub>
az configure --defaults group=<my_resource_group> workspace=<my_workspace>
```

## Install Prompt Flow VS Code Extension

Install the prompt flow extension for VS Code by following [this link](https://marketplace.visualstudio.com/items?itemName=prompt-flow.prompt-flow).

## Create Prompt Flow Connections in Local Development Environment

We need five connections one for GPT4V and another for GPT3.5-turbo.

Please create connection files from the [template](../keyword_correctness/connections/aoai_gpt4v_region.yaml) in `keyword_correctness\connections`. Replace region with the region of Azure Open AI instance.

You can use the `pf` cli to create the connections locally. A sample command to create a connection locally is shown below.

```shell
pf connection create --file keyword_correctness\connections\aoai_gpt4v_westus.yaml --set api_key=<your_api_key> api_base="https://<azure_openai_resource_name>.openai.azure.com/"
```

Refer here for more details on the [connection creation using `pf` cli](https://microsoft.github.io/promptflow/how-to-guides/manage-connections.html)

### Update connection details in the flow

After the connection is created, update the flow.dag.yaml file with the connection name, model name and the deployment name. Keep the deployment name same as the model name for simplicity.  

Sample flow.dag.yaml file for GPT3.5T is shown below.

```yaml
deployment_name: gpt-35-turbo
model: gpt-3.5-turbo

connection: aoai_gpt_35t_connection
```

For more details on using the promptflow CLI run the help comand to get a list of all the commands.

```shell
pf -h 
```

Refer to [this](https://github.com/microsoft/promptflow) repository for more info.

## Troubleshooting
- If you see any errors like `Request Header Fields Too Large` in promptflow ui after submitting jobs, please make sure to update the runtime to promptflow latest version.
- Please make sure to use the latest version of promptflow pip package.
- Please make sure that connections which are used in `flow.dag.yaml` are added in the PromptFlow.
