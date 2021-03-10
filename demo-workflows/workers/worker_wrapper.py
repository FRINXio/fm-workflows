import copy
import json
import threading
import time
import traceback
from datetime import datetime
from threading import Thread

import requests
from conductor.ConductorWorker import ConductorWorker
from frinx_rest import conductor_url_base, conductor_headers

DEFAULT_TASK_DEFINITION = {
    "name": "",
    "retryCount": 0,
    "ownerEmail":"example@example.com",
    "timeoutSeconds": 60,
    "timeoutPolicy": "TIME_OUT_WF",
    "retryLogic": "FIXED",
    "retryDelaySeconds": 0,
    "responseTimeoutSeconds": 10
}

conductor_task_url = conductor_url_base + "/metadata/taskdefs"

class FrinxConductorWrapper(ConductorWorker):
    """
    Adds:
    - Exception handling: auto failing tasks on exception
    - Task registration function
    - Batch polling for tasks instead of simple polling
    - Dedicated queue scanning thread to only perform polling if there are tasks waiting in queue
    """

    def __init__(self, server_url, thread_count, polling_interval, worker_id=None, headers=None):
        # Synchronizes access to self.queues by producer thread (in read_queue) and consumer threads (in tasks_in_queue)
        self.lock = threading.Lock()
        self.queues = {}
        super().__init__(server_url, thread_count, polling_interval, worker_id, headers)

    def start_queue_polling(self):
        print("Starting queue polling thread")
        thread = Thread(target=self.read_queues)
        thread.daemon = True
        thread.start()

    def read_queues(self):
        failCount = 0
        print("Queue polling thread started")
        while True:
            try:
                time.sleep(float(self.polling_interval))
                self.lock.acquire()
                queuesTemp = self.taskClient.getTasksInQueue("all")
                print(f'Queues polled: {queuesTemp}')
                self.queues = queuesTemp
                failCount = 0
            except Exception as err:
                print(f'Unable to read queue info. Error count: {failCount}', err)
                self.queues = {}
                failCount =+ 1
                if (failCount > 10):
                    print(f'Exiting, unable to read queue info')
                    exit(1)
            finally:
                self.lock.release()


    # register task metadata into conductor
    def register(self, task_type, task_definition=None):
        if task_definition is None:
            task_definition = DEFAULT_TASK_DEFINITION

        print('Registering task ' + task_type + ' : ' + str(task_definition))
        task_meta = copy.deepcopy(task_definition)
        task_meta["name"] = task_type
        try:
            r = requests.post(conductor_task_url,
                              data=json.dumps([task_meta]),
                              headers=conductor_headers)
            # response_code = r.status_code
        except Exception as err:
            print('Error while registering task ' + traceback.format_exc())
            raise err

    def poll_and_execute(self, taskType, exec_function, domain=None):
        poll_wait = 5000
        while True:
            time.sleep(float(self.polling_interval))

            # If there are not tasks indicated in queues, skip actual polling
            if (not self.tasksInQueue(taskType, domain)):
                continue

            print(self.timestamp() + ' Polling for task: ' + taskType + ' with wait ' + str(poll_wait))
            polled = self.taskClient.pollForBatch(taskType, 1, poll_wait, self.worker_id, domain)
            if polled is not None:
                print(self.timestamp() + ' Polled batch for ' + taskType + ':' + str(len(polled)))
                for task in polled:
                    print(self.timestamp() + ' Polled ' + taskType + ': ' + task['taskId'])
                    if self.taskClient.ackTask(task['taskId'], self.worker_id):
                        self.execute(task, exec_function)

    # Check if latest local copy of queues contains >0 number of tasks for current queue
    def tasksInQueue(self, taskType, domain=None):
        print(f'Checking tasks in queue {taskType}')
        self.lock.acquire()

        try:
            queueName = taskType

            if queueName in self.queues:
                numberOfTasksInQueue = self.queues[queueName]
            else:
                numberOfTasksInQueue = 0

            print(f'Tasks in queue: {taskType} : {numberOfTasksInQueue}')

            if numberOfTasksInQueue > 0:
                return True

        except Exception as err:
            print(f'Unable to check queue info. Polling', err)
            return True

        finally:
            self.lock.release()

        return False

    def timestamp(self):
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S:%f")

    def execute(self, task, exec_function):
        try:
            print(self.timestamp() + ' Executing task: ' + task['taskId'])
            resp = exec_function(task)
            if resp is None:
                raise Exception(
                    'Task execution function MUST return a response as a dict with status and output fields')
            task['status'] = resp['status']
            task['outputData'] = resp.get('output', {})
            task['logs'] = resp.get('logs', "")
            self.taskClient.updateTask(task)
        except Exception as err:
            print('Error executing task: ' + traceback.format_exc())
            task['status'] = 'FAILED'
            task['outputData'] = {'Error executing task:': str(task),
                                  'exec_function': str(exec_function), }
            task['logs'] = ["Logs: %s" % traceback.format_exc()]

            try:
                self.taskClient.updateTask(task)
            except Exception as err2:
                # Can happen when task timed out
                print('Unable to update task: ' + task['taskId'] + ': ' + traceback.format_exc())

if __name__ == '__main__':
    main()
