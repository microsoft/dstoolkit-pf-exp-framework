"""OpenAI processing tool."""
from jinja2 import Template
from promptflow import tool
import os
from dotenv import load_dotenv
import logging
from openai import AzureOpenAI
from typing import Optional
from promptflow.connections import AzureOpenAIConnection
import openai
import sys
import time
load_dotenv()

os.environ["PF_LOGGING_LEVEL"] = "DEBUG"
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Changing AzureOpenAI max retries to 10, default value is 2
OPENAI_MAX_RETRIES = 10

def make_openai_call(client: AzureOpenAI,
                     deployment_name: str,
                     messages: list,
                     prompt_message: dict,
                     row_index: int,
                     max_tokens: Optional[int],
                     seed: Optional[int],
                     top_p: Optional[float],
                     temperature: Optional[float],
                     openai_url:Optional[str]) -> dict:
    """Function to make openai api call

    Args:
        client (AzureOpenAI): AzureOpenAI client connection
        deployment_name (str): deployment name
        messages (list): messages list 
        prompt_message (dict) : prompt message dict 
        max_tokens (int): max token count
        seed (int, optional): seed value. 
        top_p (float, optional): top_p value. 
        temperature (float, optional): temperature value. 

    Returns:
        dict: Returns the response from openai in dict format
    """
    
    try:
        logger.info("Making openai call")
        response = None
        
        if client is None:
            raise Exception("OpenAI client is None")
        
        start_time = time.time()
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages,
            max_tokens=max_tokens,
            seed=seed,
            top_p=top_p,
            temperature=temperature
        )
        time_taken = time.time() - start_time
        print(f"Row: {row_index} OpenAI call took {time_taken} seconds for url {openai_url}", file=sys.stderr)
        
        if response is None:
            print(f"Row {row_index} Chat Completions response is None {str(e)}",file="sys.stderr")
            raise Exception("Chat Completions response is None")
        
        if not isinstance(response, dict):
            response = response.model_dump()
        
        choices = response.get("choices", [])
        
        if len(choices) == 0:
            print(f"Row {row_index},Error in generating keyword correctness response {str(e)}",file="sys.stderr")
            raise Exception("Error in generating keyword correctness response")
        else:
            message = choices[0].get("message", {})
            content = message.get("content", "No value in content")
            usage = response.get("usage", {})
            result = {
                "status": "Success",
                "output": content,
                "prompt_message": prompt_message,
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens",0),
                "total_tokens": usage.get("total_tokens",0),
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens,
                "seed": seed,
                "error": "",
                "openai_url": openai_url,
                "time_taken": time_taken
            }
    except openai.APIError as e:
        logger.exception(f"Row {row_index} OpenAI API Error occurred in make_openai_call")
        raise
    except Exception as e:
        logger.exception(f"Row {row_index} Exception occurred in make_openai_call")
        raise
    return result


def create_openai_client(connection: AzureOpenAIConnection, deployment_name:str) -> AzureOpenAI:
    """Function to create openai client
    
    Args:
        connection (AzureOpenAIConnection): AzureOpenAI client connection
        deployment_name (str): deployment name 

    Returns:
        AzureOpenAI: AzureOpenAI client
    """
    logger.info("Creating openai client")
    api_key = connection.api_key
    base_url = connection.api_base
    client = AzureOpenAI(
        api_key=api_key,
        api_version=connection.api_version,
        base_url=f"{base_url}openai/deployments/{deployment_name}/extensions",
        max_retries=OPENAI_MAX_RETRIES
    )
    return client


def create_user_prompt_text(prompt_template: str,
                            keywords: dict,
                            grounding_attributes: dict,
                            fsn: str) -> str:
    """Function to create user prompt text

    Args:
        prompt_template (str): input prompt template
        keywords (dict): dict of keywords
        grounding_attributes (dict): dict of grounding attributes
        fsn (str): fsn value

    Returns:
        str: user prompt string
    """
    logger.debug("Creating user prompt text")
    with open(prompt_template, 'r') as file:
        prompt_template_text = file.read()

    if prompt_template_text is None or prompt_template_text == "":
        raise Exception("Prompt template not found")

    jinja_template = Template(prompt_template_text)
    prompt_text = jinja_template.render(
        fsn=fsn, keywords=keywords, grounding_attributes=grounding_attributes,
    )
    return prompt_text


def create_system_prompt_text() -> str:
    """Function to create system prompt text

    Returns:
        str: system prompt text
    """
    logger.debug("Creating system prompt text")
    system_prompt_file = "system_prompt.jinja2"
    with open(system_prompt_file, 'r') as file:
        prompt_template_text = file.read()

    if prompt_template_text is None or prompt_template_text == "":
        raise Exception("System prompt template not found")

    return prompt_template_text


def create_openai_chat_messages(system_prompt_text: str,
                                user_prompt_text: str,
                                images: list[str],
                                res: str) -> list:
    """Generates openai chat messages list

    Args:
        system_prompt_text (str): system prompt text
        user_prompt_text (str): user prompt text
        images (list[str]): list if image urls
        res (str): resolution of the image("auto"/"low"/"high")

    Returns:
        list: messages list
    """

    logger.debug("Creating openai chat messages")
    messages = [
        {"role": "system", "content": system_prompt_text},
        {"role": "user", "content":
            [
                {
                    "type": "text",
                    "text": user_prompt_text
                }
            ]
         }
    ]
    
    for image in images:
        url = f"data:image/jpeg;base64,{image}"
        messages[1]["content"].append({
            "type": "image_url",
            "image_url": {
                "url": url,
                "detail": res,
            },
        })
    return messages

@tool
def openai_process( row_index: int,
                    product_images: list[str],
                    prompt_template: str,
                    fsn: str,
                    keywords: dict,
                    connection_1: AzureOpenAIConnection,
                    connection_2: AzureOpenAIConnection,
                    connection_3: AzureOpenAIConnection,
                    mandatory_grounding_attributes: dict,
                    good_to_have_grounding_attributes: dict,
                    deployment_name: str,
                    temperature: Optional[float],
                    top_p: Optional[float],
                    seed: Optional[int],
                    max_tokens: Optional[int],
                    res: Optional[str] = "auto"
                    ) -> dict:
    """Prompt flow tool function to make openai call and get the response


    Args:
        product_images (list[str]): list if product images
        prompt_template (str): product template name
        fsn (str): fsn
        keywords (dict): keywords
        grounding_attributes (dict): grounding attributes
        connection (AzureOpenAIConnection): connection object
        deployment_name (str): deployment name
        temperature (Optional[float], optional): temperature. 
        top_p (Optional[float], optional): top_p.
        seed (Optional[int], optional): seed. 
        max_tokens (Optional[int], optional): maxtokens. 
        res (str, optional): res.

    Returns:
        dict: returns dict of output result
    """
    try:
        
        if len(product_images) == 0 or fsn == "" or \
            len(keywords) == 0 or  connection_1 == None or \
                connection_2 == None or connection_3 == None or  deployment_name == ""  or \
                     len(mandatory_grounding_attributes) == 0:
                raise ValueError("Missing required input params")
            
            
        connections = [connection_1, connection_2, connection_3]
        connection_index = int(row_index) % len(connections) 
        openai_url = connections[connection_index].api_base
        
        print(f"Processing row :{row_index} with {openai_url}", file=sys.stderr) 
        
        client = create_openai_client(connection=connections[connection_index],
                                      deployment_name=deployment_name)

        system_prompt_text = create_system_prompt_text()
        user_prompt_text = create_user_prompt_text(prompt_template=prompt_template,
                                                   keywords=keywords,
                                                   grounding_attributes=mandatory_grounding_attributes,
                                                   fsn=fsn)

        messages = create_openai_chat_messages(
            system_prompt_text=system_prompt_text,
            user_prompt_text=user_prompt_text,
            images=product_images,
            res=res)
        
        prompt_message = {
            "system_prompt": system_prompt_text,
            "user_prompt": user_prompt_text,
        }
        
        result = make_openai_call(client=client,
                                  deployment_name=deployment_name,
                                  messages=messages,
                                  prompt_message=prompt_message,
                                  max_tokens=max_tokens,
                                  temperature=temperature,
                                  top_p=top_p,
                                  seed=seed,
                                  row_index=row_index,
                                  openai_url = openai_url)

        logger.info(f"OpenAI call response: {result}")
    except Exception as e:
        logger.exception(f"Row {row_index} Exception occurred in openai_process")
        raise
    return result