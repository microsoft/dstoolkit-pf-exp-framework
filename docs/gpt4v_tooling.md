# Overview
This document covers the custom python tools used in experiment [step1](../docs/experiment_details.md) for making calls to GPT4V with images.

## Requirements with GPT4V usecase
*   Use of `detail` param while sending requests to GPT4V. More details about the `detaul` param can be found [here](https://platform.openai.com/docs/guides/vision). Currently `detail` param is not supported in Promptlfow LLM tool. Using low resolution in detail in param help in reducing the token count and eventually cost of the experimentation.
*   Scaling up operations in GPT4V. 
    PromptFlow LLM tool doesnot support making call to multiple connections. Custom python tool used in this repo shows how to make calls to multiple openai connections in one flow.


## Components in GPT4V flow

### Image Processing Custom Python tool
`Image process tool` code is present [here.](../keyword_correctness/flows/experiment_step1/image_processing.py)
Custom python tool `process_image` take the list of image urls. It resizes the images if image width or height is greater than 1024. Resized images are convered to base64 string and passed to the next step in the flow.


### OpenAI process custom python tool
It has two main purpose:

1. #### Making calls to GPT4V with `detail` param

    The `detail` param is added while constructing the messages for GTP4V call. This is required to set the image resolution to high or low based on the use case in the experimentation.

    Following code in function `create_openai_chat_messages` adds the detail param
    ```py
    for image in images:
            url = f"data:image/jpeg;base64,{image}"
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": url,
                    "detail": res,
                },
            })
    ```

2.  #### Using multiple openai connections in the flow
    Processing of large number of images with GPT4V may take couple of hours. From our estimation, processing 10K images with one openai instance  takes around 20 hours. Running expriments with more than 200K records with multiple variants would take lot of time. To reduce the execution time of these experiments we used multiple openai connections in the custom python tool and used those connections in round robin basis.

    To use multiple connection we introduced `row_index` as one the column in the input recordset.

    Code that selects the openai connection in round robin fashion is located in function `openai_process`

    ```py
    connections = [connection_1, connection_2, connection_3, connection_4, connection_5]
        connection_index = int(row_index) % len(connections) 
        openai_url = connections[connection_index].api_base
        
        client = create_openai_client(connection=connections[connection_index],
                                      deployment_name=deployment_name)
    ```

    `flow.dag.yaml` should also contain these connections as input params.

    To use these connections, please make sure that these connections are created in AML workspace.   
    In this example we have used five connections, but the number of connections can be changed depending on the use case. If number of connections are changed, following files need to be mofidifed.:
    *   [flow.dag.yaml](../keyword_correctness/flows/experiment_step1/flow.dag.yaml)
    *   [openai_process.py](../keyword_correctness/flows/experiment_step1/openai_process.py)