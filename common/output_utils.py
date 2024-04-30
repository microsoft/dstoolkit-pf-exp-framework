import csv
import json
import logging
import requests
from pathlib import Path
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

resource_group = os.getenv('RESOURCE_GROUP')
workspace_name = os.getenv('WORKSPACE')
subscription_id = os.getenv('SUBSCRIPTION_ID')

# Get a logger which allows us to log events that occur when running the program.
logger = logging.getLogger("myLogger")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s %(message)s")
ch = logging.StreamHandler()
ch.setFormatter(formatter)
ch.setLevel(logging.DEBUG)
if not logger.handlers:
    logger.addHandler(ch)

# interactive_auth = InteractiveLoginAuthentication(tenant_id=tenant_id)
# ws = Workspace.get(workspace_name, subscription_id=subscription_id, resource_group=resource_group, auth=interactive_auth)
ws = Workspace.get(
    workspace_name, subscription_id=subscription_id, resource_group=resource_group)
region = ws.location
default_datastore = ws.get_default_datastore()

# Get run infor for the given run_id


def get_run_info(run_id):
    logger.info(f"Getting Run Info for Run: {run_id}")
    run = ws.get_run(run_id=run_id)
    display_name = run.display_name
    input_run_id = run.properties.get('azureml.promptflow.input_run_id')
    return display_name, input_run_id

# Get the output asset id for the given run_id and asset_name


def get_output_asset_id(run_id, asset_name):
    logger.info(f"Getting Output Asset Id for Run {run_id}")
    if region == "centraluseuap":
        url = f"https://int.api.azureml-test.ms/history/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/rundata"
    else:
        url = f"https://ml.azure.com/api/{region}/history/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/rundata"
    payload = {
        "runId": run_id,
        "selectRunMetadata": True
    }
    response = requests.post(
        url, json=payload, headers=ws._auth.get_authentication_header())
    if response.status_code != 200:
        raise Exception(
            f"Failed to get output asset id for run {run_id} because RunHistory API returned status code {response.status_code}. Response: {response.text}")
    output_asset_id = response.json(
    )["runMetadata"]["outputs"][asset_name]["assetId"]
    return output_asset_id

# Get the asset path for the given asset_id


def get_asset_path(asset_id):
    logger.info(f"Getting Asset Path for Asset Id {asset_id}")
    if region == "centraluseuap":
        url = f"https://int.api.azureml-test.ms/data/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/dataversion/getByAssetId"
    else:
        url = f"https://ml.azure.com/api/{region}/data/v1.0/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.MachineLearningServices/workspaces/{workspace_name}/dataversion/getByAssetId"
    payload = {
        "value": asset_id,
    }
    response = requests.post(
        url, json=payload, headers=ws._auth.get_authentication_header())
    if response.status_code != 200:
        raise Exception(
            f"Failed to get asset path for asset id {asset_id} because Data API returned status code {response.status_code}. Response: {response.text}")
    data_uri = response.json()["dataVersion"]["dataUri"]
    relative_path = data_uri.split("/paths/")[-1]
    return relative_path

# Get the flow artifact relative path for the given run_id


def get_flow_artifact_relative_path(run_id):
    logger.info(f"Getting Flow Artifact Relative Path for Run {run_id}")
    try:
        flow_artifact_asset_id = get_output_asset_id(run_id, "debug_info")
        relative_path = get_asset_path(flow_artifact_asset_id)
        relative_path += "flow_artifacts/"
        return relative_path
    except Exception as e:
        logger.warning(
            "`debug_info` output assets is not available, maybe because the job ran on old version runtime, trying to get `flow_outputs` output asset instead.")
        output_asset_id = get_output_asset_id(run_id, "flow_outputs")
        relative_path = get_asset_path(output_asset_id)
        return relative_path.replace("flow_outputs", "flow_artifacts")

# Download flow artifacts for the given run_id


def download_flow_artifacts(run_id, blob_prefix):
    logger.info(f"Downloading Flow Artifacts for Run {run_id}")
    target_dir = f"./downloads/{run_id}"
    default_datastore.download(target_dir, prefix=blob_prefix, overwrite=True)
    return target_dir

# Load flow artifacts of the run from the given local_dir


def load_flow_artifacts(local_dir, run_display_name):
    logger.info(
        f"Loading Flow Artifacts of {run_display_name} from {local_dir}")
    flow_artifacts = {}
    p = Path(local_dir)
    for file_path in p.glob("**/*.jsonl"):
        with open(file_path) as fp:
            for line in fp:
                line_record = json.loads(line)
                line_number = line_record.get("line_number")
                run_info = line_record.get("run_info") or {}
                status = run_info.get("status")
                outputs = run_info.get("output") or {}
                inputs = run_info.get("inputs") or {}
                modified_inputs = {f"inputs.{k}": v for k, v in inputs.items()}
                record = {
                    "Line number": line_number,
                    "Run": run_display_name,
                    "Status": status,
                    **modified_inputs,
                    **outputs
                }
                flow_artifacts[line_number] = record
    return flow_artifacts

# Get required info for the given run_id


def get_required_info(run_id):
    logger.info(f"Processing Run: {run_id}")
    display_name, input_run_id = get_run_info(run_id)
    flow_artifact_relative_path = get_flow_artifact_relative_path(run_id)

    target_dir = download_flow_artifacts(run_id, flow_artifact_relative_path)
    flow_artifacts = load_flow_artifacts(target_dir, display_name)
    return {
        "run_id": run_id,
        "display_name": display_name,
        "input_run_id": input_run_id,
        "flow_artifacts": flow_artifacts
    }

# Update downstream flow artifacts with the given display_name


def update_downstread_flow_artifacts(flow_artifacts, display_name):
    updated_flow_artifacts = {}
    for line_number, line_record in flow_artifacts.items():
        updated_line_record = {}
        for k, v in line_record.items():
            if k == "Run" or k == "Status" or k == "Line number":
                continue
            else:
                updated_line_record[f"{k}({display_name})"] = v
        updated_flow_artifacts[line_number] = updated_line_record
    return updated_flow_artifacts

# Merge flow artifacts for the given run_infos, joining flow artifacts with the same line number


def merge_flow_artifacts(run_infos: list):
    run_info_dict = {run_info["run_id"]: run_info for run_info in run_infos}
    main_flow_infos = []
    for run_id, run_info in run_info_dict.items():
        if run_info["input_run_id"] is None:
            main_flow_infos.append(run_info)
        else:
            input_run_id = run_info["input_run_id"]
            if input_run_id in run_info_dict:
                input_run_info = run_info_dict[input_run_id]
                updated_flow_artifacts = update_downstread_flow_artifacts(
                    run_info["flow_artifacts"], run_info["display_name"])
                for line_number, updated_flow_artifact in updated_flow_artifacts.items():
                    if line_number in input_run_info["flow_artifacts"]:
                        input_run_info["flow_artifacts"][line_number].update(
                            updated_flow_artifact)
            else:
                # Input Run is not included, treat this run as main flow
                main_flow_infos.append(run_info)

    merge_result = []
    for main_flow_info in main_flow_infos:
        merge_result += list(main_flow_info["flow_artifacts"].values())
    merge_result = sorted(
        merge_result, key=lambda x: f"{x['Line number']}{x['Run']}")
    return merge_result

# Convert the given jsonl file to csv file


def jsonl_to_csv(jsonl_path, csv_path):
    max_keys = []
    with open(jsonl_path, "r") as jsonl_file:
        for line in jsonl_file:
            row = json.loads(line)
            if len(row.keys()) > len(max_keys):
                max_keys = list(row.keys())

    with open(jsonl_path, "r") as jsonl_file:
        with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(max_keys)
            for line in jsonl_file:
                row = json.loads(line)
                csv_row = [row.get(key) for key in max_keys]
                writer.writerow(csv_row)


def download_output(run, output_file: str):
    if isinstance(run, str):
        run_id = run
    else:
        run_id = run.name
        
    run_infos = [get_required_info(run_id)]
    merged_result = merge_flow_artifacts(run_infos)
    
    jsonl_path = f"{output_file}.jsonl"
    csv_path = f"{output_file}.csv"
    with open(jsonl_path, "w") as fp:
        for record in merged_result:
            fp.write(json.dumps(record))
            fp.write("\n")
    logger.info(f"Saved merged result as jsonl to {jsonl_path}")
    jsonl_to_csv(jsonl_path, csv_path)
    logger.info(f"Saved merged result as csv to {csv_path}")
