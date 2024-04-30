"""Input processing tool."""
from collections import defaultdict
from typing import List, Dict
from promptflow import tool
from itertools import islice
import sys

NO_OF_GOOD_TO_HAVE_ATTRIBUTES= 10

@tool
def process_input(keywords: Dict, grounding_attributes: List[Dict]) -> Dict:
    """
    Prepare input data for LLM tool.

    Args:
        keywords (dict): Dictionary containing the product keywords and their corresponding correctness values (as per manual annotation)
        grounding_attributes (list[dict]): List of dictionaries containing the grounding attributes for the product
    Returns:
        dict: Dictionary containing product keywords list, keyword count, mandatory attributes and good to have attributes
    """
    keywords_list = list(keywords.keys())
    keywords_count = len(keywords_list)

    # Validate if grounding attributes have all the required keys
    required_keys = ["name", "value", "priority", "fillRate"]
    for attribute in grounding_attributes:
        missing_keys = [key for key in required_keys if key not in attribute]
        if missing_keys:
            raise ValueError(f"Required key(s) missing from grounding attribute {attribute}: {', '.join(missing_keys)}")

    grounding_attributes_clean = [attr for attr in grounding_attributes if attr["name"] != "keywords" and attr["value"] is not None]

    mandatory_attributes = [attr for attr in grounding_attributes_clean if attr.get("priority") and attr["priority"].lower() == "mandatory"]
    mandatory_attributes_defaultdict = defaultdict(list)
    for attr in mandatory_attributes:
        mandatory_attributes_defaultdict[attr["name"]].append(attr["value"])
    mandatory_attributes_dict = {k: ', '.join([str(x) for x in v]) for k, v in mandatory_attributes_defaultdict.items()}

    good_to_have_attributes = [attr for attr in grounding_attributes_clean if attr.get("priority") and attr["priority"].lower() == "good_to_have"]
    # Sort the filtered list in descending order based on fillRate
    good_to_have_attributes.sort(key=lambda x: x["fillRate"], reverse=True)
    good_to_have_attributes_defaultdict = defaultdict(list)
    for attr in good_to_have_attributes:
        good_to_have_attributes_defaultdict[attr["name"]].append(attr["value"])
    good_to_have_attributes_dict = {k: ', '.join([str(x) for x in v]) for k, v in good_to_have_attributes_defaultdict.items()}

    if 'description' in good_to_have_attributes_dict:
        keys = list(good_to_have_attributes_dict.keys())
        if keys.index('description') >= NO_OF_GOOD_TO_HAVE_ATTRIBUTES:
            keys.remove('description')
            keys.insert(NO_OF_GOOD_TO_HAVE_ATTRIBUTES-1, 'description')
            good_to_have_attributes_dict = {k: good_to_have_attributes_dict[k] for k in keys}
    else:
        print(f"Description not found in good to have attributes", file=sys.stderr)
    
    
    print(f"No of elements in good to have list {len(good_to_have_attributes_dict)}", file=sys.stderr) 
    return {
            "keywords": keywords_list,
            "keywords_count": keywords_count,
            "mandatory_grounding_attributes": mandatory_attributes_dict,
            "good_to_have_grounding_attributes": good_to_have_attributes_dict
        }
