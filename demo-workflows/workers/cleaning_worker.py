import copy
import logging

from logging_helpers import logging_handler
from util import completed_response

log = logging.getLogger(__name__)

subworkflow_template = {
    "name": "sub_task",
    "taskReferenceName": "",
    "type": "SUB_WORKFLOW",
    "subWorkflowParam": {"name": "", "version": 1},
}


def parse_resources_to_dynamic_tasks(
    resource, pool_id, sub_workflow_name, dynamic_tasks_i, dynamic_tasks
):
    # if resource have nested pool then cleanup nested pool and after that delete resource
    if sub_workflow_name == "Resource_or_pool_deallocation" and resource["NestedPool"]:
        dynamic_tasks_i[resource["id"] + str(0)] = {
            "pool_tag": resource["NestedPool"]["Tags"]["0"]["Tag"]
        }
        task_body = copy.deepcopy(subworkflow_template)
        task_body["taskReferenceName"] = resource["id"] + str(0)
        task_body["subWorkflowParam"]["name"] = "Cleanup_pool"
        task_body["optional"] = False
        dynamic_tasks.append(task_body)

    # separating multi path resources and single path resources
    if (
        "path" in resource["AlternativeId"]
        and "/" not in resource["AlternativeId"]["path"]
    ):
        dynamic_tasks_i[resource["id"]] = {
            "pool_id": pool_id,
            "resource": resource["Properties"],
            "alt_id": resource["AlternativeId"],
            "type": "multi_path_resource",
        }
    else:
        dynamic_tasks_i[resource["id"]] = {
            "pool_id": pool_id,
            "resource": resource["Properties"],
            "alt_id": resource["AlternativeId"],
            "type": "resource",
        }
    task_body = copy.deepcopy(subworkflow_template)
    task_body["taskReferenceName"] = resource["id"]
    task_body["subWorkflowParam"]["name"] = sub_workflow_name
    task_body["optional"] = False
    dynamic_tasks.append(task_body)

    return dynamic_tasks_i, dynamic_tasks


@logging_handler(log)
def get_resources_as_dynamic_fork_tasks(task, logs):
    """Generate dict and list needed for execution of a dynamic
    fork task in Conductor. Takes an input list containing
    dicts with resources and resource alternative ids. Used to check resource status.

    Args:
        task: dict
        It has to contain a resources or pools of resources with alternate ids.
        logs (obj): logs object to be serialized and displayed

    Returns:
        Standard worker response with operation status and
        data for execution of a dynamic fork task.
    """
    resources = task["inputData"]["data"]
    wf_type = task["inputData"]["type"]
    cursor = resources["0"]["cursor"]
    dynamic_tasks_i = {}
    dynamic_tasks = []
    if wf_type == "verification_and_delete":
        sub_workflow = "Resource_deallocation_helper"
    elif wf_type == "delete_with_nested_pools":
        sub_workflow = "Resource_or_pool_deallocation"
    else:
        sub_workflow = "Resource_lookup_helper"
    for i in reversed(list(resources)):
        if ("node" in resources[i]) and (
            (
                "AlternativeId" in resources[i]["node"]
                and "path" in resources[i]["node"]["AlternativeId"]
            )
            or (wf_type == "delete_with_nested_pools")
        ):
            dynamic_tasks_i, dynamic_tasks = parse_resources_to_dynamic_tasks(
                resources[i]["node"],
                resources[i]["node"]["ParentPool"]["id"],
                sub_workflow,
                dynamic_tasks_i,
                dynamic_tasks,
            )

    return completed_response(
        {
            "dynamic_tasks_i": dynamic_tasks_i,
            "dynamic_tasks": dynamic_tasks,
            "cursor": cursor,
        },
    )


@logging_handler(log)
def get_empty_pools_as_dynamic_fork_tasks(task, logs):
    """Generate dict and list needed for execution of a dynamic
    fork task in Conductor. Takes an input list containing
    dicts with pools ids. Used to delete empty pools.

    Args:
        task: dict
        It has to contain empty pools ids.
        logs (obj): logs object to be serialized and displayed

    Returns:
        Standard worker response with operation status and
        data for execution of a dynamic fork task.
    """
    pools = task["inputData"]["pools"]
    dynamic_tasks_i = {}
    dynamic_tasks = []
    for i in pools:
        if "Tags" in pools[i] and [i == "do_not_delete" for i in pools[i]["Tags"]]:
            continue
        else:
            dynamic_tasks_i[pools[i]["id"]] = {
                "pool_id": pools[i]["id"],
                "type": "pool",
            }
            task_body = copy.deepcopy(subworkflow_template)
            task_body["taskReferenceName"] = pools[i]["id"]
            task_body["subWorkflowParam"]["name"] = "Resource_or_pool_deallocation"
            task_body["optional"] = False
            dynamic_tasks.append(task_body)

    return completed_response({"dynamic_tasks_i": dynamic_tasks_i, "dynamic_tasks": dynamic_tasks}
    )


def start(cc):
    cc.register(
        "Get_resources_as_dynamic_fork_tasks",
        {
            "description": '{"description": "Prepare dynamic fork to check resource status."}',
            "retryCount": 0,
            "timeoutSeconds": 60,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "responseTimeoutSeconds": 10,
            "inputKeys": ["pools"],
            "outputKeys": ["dynamic_tasks_i", "dynamic_tasks", "cursor"],
        },
        get_resources_as_dynamic_fork_tasks,
    )

    cc.register(
        "Get_empty_pools_as_dynamic_fork_tasks",
        {
            "description": '{"description": "Prepare dynamic fork tasks to delete empty pools."}',
            "retryCount": 0,
            "timeoutSeconds": 60,
            "timeoutPolicy": "TIME_OUT_WF",
            "retryLogic": "FIXED",
            "retryDelaySeconds": 0,
            "responseTimeoutSeconds": 10,
            "inputKeys": ["pools"],
            "outputKeys": ["dynamic_tasks_i", "dynamic_tasks"],
        },
        get_empty_pools_as_dynamic_fork_tasks,
    )
