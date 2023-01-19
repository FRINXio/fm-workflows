import copy
import util
import time

import json
from typing import Any

subworkflow_template = {
    "name": "sub_task",
    "expectedName": "sub_task",
    "expectedType": "SUB_WORKFLOW",
    "taskReferenceName": "",
    "type": "SUB_WORKFLOW",
    "subWorkflowParam": {"name": "", "version": 1},
}


def execute_dummy_task(task):
    task_input = task["inputData"]
    wait_time = int(task_input["wait_time"]) or 0

    # time.sleep(wait_time)

    start = time.time()
    # file = "dummy_data.json"
    file = "dummy_bpe9_pe_asr9k_native_response.json"
    with open(file, "r") as read_content:
        data = json.load(read_content)

    # data = {k:k for k in range(100_000)}

    # data = {"lalala":"bububu"}  #small data

    end = time.time()
    # return_logs.info(f"took:{(end - start)}")

    return util.completed_response(data)

def execute_dummy_subworkflow_generator(task):
    try:
        task_input = task["inputData"]

        dynamic_tasks_i = {}
        dynamic_tasks = []
        sub_workflow: str = task_input["task"]

        for index in range(int(task_input["number_of_sub_workflows"])):
            unique_task_name = f"task_{index}"

            dynamic_tasks_i[unique_task_name] = {"wait_time": task_input["wait_time"]}

            task_body = copy.deepcopy(subworkflow_template)
            task_body["taskReferenceName"] = unique_task_name
            task_body["subWorkflowParam"]["name"] = sub_workflow
            dynamic_tasks.append(task_body)

        output = {}
        output["dynamic_tasks_i"] = dynamic_tasks_i
        output["dynamic_tasks"] = dynamic_tasks
        return util.completed_response(output)
    except Exception:
        raise

def start(cc) -> None:
    cc.register(
        "dummy_task",
        {
            "description": '',
            "inputKeys": [
                "wait_time",
            ],
            "outputKeys": [
                "data",
            ],
        },
        execute_dummy_task
        # limit_to_thread_count=None, #it should coresponde to concurrentExecLimit not set at all?
    )

    cc.register(
        "DummySubworkflowGenerator",
        {
            "description": '',
            "inputKeys": [
                "number_of_sub_workflows",
                "wait_time",
                "task",
            ],
            "outputKeys": [
                "dynamic_tasks",
                "dynamic_tasks_i",
            ],
        },
        execute_dummy_subworkflow_generator
    )
