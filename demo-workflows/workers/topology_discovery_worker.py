import util
import requests

TOPOLOGY_DISCOVERY_BASE_URL = "http://fm_topology-discovery:5000/api"


def arangodb_create_backup_and_delete_old_backups(task):
    response = requests.post(TOPOLOGY_DISCOVERY_BASE_URL + "/backup_arangodb")
    return util.completed_response(response.json())


def start(cc):
    cc.register('ArangoDB_create_backup_and_delete_old_backups', {
        "description": '{"description": "ArangoDB create backup and delete old backups"}',
        "inputKeys": [],
        "outputKeys": [
            "created_db_name",
            "list_of_deleted_db"
        ]
    }, arangodb_create_backup_and_delete_old_backups)

