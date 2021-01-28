import os
import requests
import traceback
import json
from frinx_rest import conductor_url_base, conductor_headers

workflow_import_url = conductor_url_base + '/metadata/workflow'


def import_workflows(path):
    if os.path.isdir(path):
        print("\nIt is a directory")
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_file():
                    try:
                        print('Importing workflow ' + entry.name)
                        with open(entry, 'r') as payload_file:
                            # api expects array in payload
                            payload = []
                            payload_json = json.load(payload_file)
                            payload.append(payload_json)
                            r = requests.put(workflow_import_url,
                                             data=json.dumps(payload), headers=conductor_headers)
                            print("Response:", r.status_code)
                    except Exception as err:
                        print('Error while registering task ' + traceback.format_exc())
                        raise err
                elif entry.is_dir():
                    import_workflows(entry.path)
                else:
                    print(entry)
    else:
        print("Path to workflows " + path + " is not a directory.")