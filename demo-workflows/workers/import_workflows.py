import os
import requests
import traceback
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
                        with open(entry, 'rb') as payload:
                            r = requests.post(workflow_import_url,
                                              data=payload, headers=conductor_headers)
                    except Exception as err:
                        print('Error while registering task ' + traceback.format_exc())
                        raise err
                elif entry.is_dir():
                    import_workflows(entry.path)
                else:
                    print(entry)
    else:
        print("Path not a directory")