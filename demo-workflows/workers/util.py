
FAILED_STATUS = "FAILED"
COMPLETED_STATUS = "COMPLETED"


def completed_response(response_body=None):
    """
    Use for workflow responses with COMPLETED status.

        Args:
            response_body (obj): anything we want to return from a workflow

        Return:
            response dictionary: {"status": "COMPLETED", "output": <response_body>}

    """
    return finalize_response(COMPLETED_STATUS, response_body)


def failed_response(response_body=None):
    """
    Use for workflow responses with FAILED status. Response_body should contain error message.

        Args:
            response_body (obj): anything we want to return from a workflow

        Return:
            response dictionary: {"status": "FAILED", "output": <response_body>}

    """
    return finalize_response(FAILED_STATUS, {"error_message": response_body})


def finalize_response(status, response_body):
    return {"status": status, "output": response_body if response_body else {},"logs": []}
