"""This module contains helper functions and objects for logging."""
import logging
import io

log_stream = io.StringIO()

# Format the log message and set the module to log all messages at or above INFO level.
_format = "%(levelname)s %(funcName)s - %(message)s"

logging.basicConfig(
    stream=log_stream, format=_format, level=logging.INFO
)


def logging_handler(log):
    def logging_output_decorator(task_function):
        def function_wrapper(task):
            string_io = io.StringIO()
            stream_handler = logging.StreamHandler(string_io)
            stream_handler.setLevel(logging.INFO)
            log.addHandler(stream_handler)

            output = task_function(task, string_io)

            log.removeHandler(string_io)
            return output
        return function_wrapper
    return logging_output_decorator


def serialize_logs(stream):
    # Format the log stream to a json-serializable object.
    log_stream_serialized = stream.getvalue().split("\n") if stream else list()
    log_stream_serialized = list(filter(None, log_stream_serialized))

    return log_stream_serialized