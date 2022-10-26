WORKFLOW_MANAGER_SCHEDULER_URL = "http://workflow-proxy:8088/schedule"

WORKFLOW_MANAGER_SCHEDULER_LIST = [
    {
        "Arangodb_create_backup_and_delete_old_backups": {
            "workflowName": "Arangodb_create_backup_and_delete_old_backups",
            "workflowVersion": "1",
            "workflowContext": {"delete_age": "24"},
            "name": "Arangodb_create_backup_and_delete_old_backups:1",
            "cronString": "0 * * * *",
            "enabled": True,
        }
    }
]
