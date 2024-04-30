import json

from azure.identity import DefaultAzureCredential, AzureCliCredential
from dotenv import load_dotenv
from promptflow.entities import Run
import os
import time
from typing import Optional
from entities import Run as FrameworkRun

os.environ["PF_LOGGING_LEVEL"] = "DEBUG"


class PromptFlowUtils:

    def __init__(self):
        self.initialize_envs()
        self._pf = None

    def initialize_envs(self):
        load_dotenv()
        self.resource_group = os.getenv('RESOURCE_GROUP')
        self.workspace = os.getenv('WORKSPACE')
        self.subscription_id = os.getenv('SUBSCRIPTION_ID')

    def initialize_pf_client(self, cloud: bool = False) -> None:
        try:
            if not cloud:
                from promptflow import PFClient
                print(f"Initializing Local PFClient")
                self._pf = PFClient()
                if self._pf is None:
                    print("Error while initializing Local PFClient")
            else:
                from promptflow.azure import PFClient
                print(f"Initializing Cloud PFClient")
                credential = self.get_credentials()
                self._pf = PFClient.from_config(credential=credential)
                if self._pf is None:
                    print("Error while initializing Cloud PFClient")
                print("Able to init pfclient from config")
        except Exception as e:
            client_config = {
                "subscription_id": self.subscription_id,
                "resource_group": self.resource_group,
                "workspace_name": self.workspace,
            }
            if client_config["subscription_id"].startswith("<"):
                print(
                    "please update your <SUBSCRIPTION_ID> <RESOURCE_GROUP> <AML_WORKSPACE_NAME> in notebook cell"
                )
                raise e
            else:
                config_path = "../.azureml/config.json"
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                with open(config_path, "w") as fo:
                    print(f"Writing config to {config_path}")
                    fo.write(json.dumps(client_config))
                self._pf = PFClient.from_config(
                    credential=credential, path=config_path)
                if self._pf is None:
                    print(f"Error while initializing PFClient")
                print("Able to init pfclient from config")

    def get_credentials(self):
        try:
            credential = AzureCliCredential(process_timeout=60)
            credential.get_token("https://management.azure.com/.default")
            print(f"Able to get credentials")
            return credential
        except Exception as e:
            print(f"Error while getting credentials {e}")

    def show_run_details(self, run_name: str):
        details = self._pf.runs.get_details(name=run_name)
        return details

    def show_run_metrics(self, run_name: str):
        metrics = self._pf.runs.get_metrics(name=run_name)
        return metrics

    def get_run(self, run_name: str):
        return self._pf.runs.get(run = run_name)

    def visualize_runs(self, run_ids: list[str]):
        self._pf.runs.visualize(run_ids)

    def test(self, flow_dir: str):
        result = self._pf.test(flow=flow_dir)
        return result
    
    def execute(self, current_run: FrameworkRun) -> Run:
        variants = current_run.variants or [None]
        linked_runs = current_run.linked_runs or [None]
        runs_created = [self._create_run(current_run=current_run,
                                         variant=variant,
                                         linked_run=linked_run)
                        for variant in variants for linked_run in linked_runs]

        return runs_created

    def _generate_run_name(self, flow_id: str, run_suffix: str, 
                           variant: Optional[str] = None, linked_run: Optional[str] = None):
        variant_name = None
        linked_run_name = None
        tag_name = os.getenv('RUN_NAME_TAG', 'unknown_rockstar')
        if (variant is not None):
            import re
            match = re.search(r'\.(\w+)}', variant)
            if match:
                variant_name = match.group(1)
        if (linked_run is not None):
            parts = linked_run.split('_')
            linked_run_name = '_'.join(parts[1:-1])
        run_name_generator_array = [
            tag_name, flow_id, variant_name, linked_run_name, run_suffix]
        return "_".join([str(x) for x in run_name_generator_array if x is not None])
    
    def _gen_data_from_linked_run(self, linked_run: Optional[str] = None):
        if linked_run is not None:
            return f"azureml:azureml_{linked_run}_output_data_flow_outputs:1"
        else:
            return None
        
    def _create_run(self, current_run: FrameworkRun,
                    variant: Optional[str] = None,
                    linked_run: Optional[str] = None):

        name = self._generate_run_name(current_run.flow.flow_id,
                                       current_run.run_suffix, variant, linked_run)
        base_run = Run(
            flow=current_run.flow.flow_dir,
            data=current_run.data_id or self._gen_data_from_linked_run(linked_run),
            name=name,
            display_name=name,
            variant=variant,
            run=linked_run,
            tags=current_run.tags,
            column_mapping=current_run.flow.column_mapping, 
            environment_variables=current_run.env_vars
        )
        created_run = self._pf.runs.create_or_update(
            run=base_run, runtime=current_run.runtime)
        print(f"Run {name} created, Status : {created_run.status}")
        return created_run

    def wait_for_run_completion(self, runs: list[Run], time_to_sleep=1):
        status = "Running"
        runs_count = len(runs)
        allPassed = True
        while runs_count > 0:
            for run in runs:
                updated_run = self._pf.runs.get(run.name)
                print(
                    f"Checking Status of Run {updated_run.name}  -> {updated_run.status}")
                if updated_run.status == "Completed":
                    runs_count -= 1
                if updated_run.status == "Failed":
                    allPassed = False
                    runs_count -= 1
            time.sleep(time_to_sleep)

        print("All runs status check is done")
        return allPassed

    def display_local_runs(self, runs):
        from tabulate import tabulate
        for run in runs:
            run_details = self.show_run_details(run_id=run.name)
            run_details.to_csv(f"./runs/{run.name}.csv")
            table = tabulate(run_details, headers='keys', tablefmt='psql')
            print(f"Run details: {table}")
