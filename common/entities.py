from typing import Optional


class Flow:
    def __init__(self, flow_id, flow_name, flow_dir, column_mapping, variants):
        """
        Initialize a Flow object.

        Args:
            flow_id (int): The ID of the flow.
            flow_name (str): The name of the flow.
            flow_dir (str): The directory of the flow.
            column_mapping (dict): The mapping of columns.
            variants (list): The variants of the flow.
        """
        self.flow_id = flow_id
        self.flow_name = flow_name
        self.flow_dir = flow_dir
        self.column_mapping = column_mapping
        self.variants = variants
        
class Run:
    def __init__(self, flow: Flow, 
                 runtime: str, 
                 run_suffix: str, 
                 data_id: Optional[str] = None, 
                 tags: Optional[dict] = None, 
                 variants: Optional[list[str]] = None,
                 linked_runs: Optional[list[str]] = None, 
                 env_vars: Optional[dict[str, str]]= None):
        """
        Initialize a Run object.

        Args:
            flow (Flow): The flow associated with the run.
            runtime (str): The runtime of the run.
            run_suffix (str): The suffix of the run.
            data_id (str, optional): The ID of the data. Defaults to None.
            tags (dict, optional): The tags associated with the run. Defaults to None.
            variants (list, optional): The variants of the run. Defaults to None.
            linked_runs (list, optional): The linked runs. Defaults to None.
            env_vars (dict, optional): The environment variables. Defaults to None.
        """
        self.flow = flow
        self.data_id = data_id
        self.runtime = runtime
        self.tags = tags
        self.variants = variants
        self.run_suffix = run_suffix
        self.linked_runs = linked_runs
        self.env_vars = env_vars