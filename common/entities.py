from typing import Optional


class Flow:
    def __init__(self, flow_id, flow_name, flow_dir, column_mapping, variants):
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
        self.flow = flow
        self.data_id = data_id
        self.runtime = runtime
        self.tags = tags
        self.variants = variants
        self.run_suffix = run_suffix
        self.linked_runs = linked_runs
        self.env_vars = env_vars