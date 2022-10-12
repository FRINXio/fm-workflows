import util
import requests
import json

TOPOLOGY_DISCOVERY_BASE_URL = "http://topology-discovery:5000/api"
TOPOLOGY_DISCOVERY_HEADERS = {"Content-Type": "application/json"}


def arangodb_create_backup(task):
    response = requests.post(TOPOLOGY_DISCOVERY_BASE_URL + "/arangodb-backup-create")
    return util.completed_response(response.json())


def arangodb_delete_backups(task):
    delete_age = task["inputData"]["delete_age"]
    data = {"delete_age": int(delete_age)}
    response = requests.delete(TOPOLOGY_DISCOVERY_BASE_URL + "/arangodb-backup-delete", data=json.dumps(data),
                               headers=TOPOLOGY_DISCOVERY_HEADERS)

    return util.completed_response(response.json())


def start(cc):
    cc.register('Arangodb_create_backup', {
        "description": '{"description": "ArangoDB create backup"}',
        "inputKeys": [],
        "outputKeys": [
            "db_name"
        ]
    }, arangodb_create_backup)

    cc.register('Arangodb_delete_backups', {
        "description": '{"description": "ArangoDB delete all backups which are older than param delete_age"}',
        "inputKeys": [
            "delete_age"
        ],
        "outputKeys": [
            "deleted_backups"
        ]
    }, arangodb_delete_backups)
