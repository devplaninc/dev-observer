import dataclasses
import json
import os # Added import
from abc import abstractmethod
from typing import Protocol


class Encoder(Protocol):
    @abstractmethod
    def encode(self, msg: "StructuredMessage"):
        ...

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        # Handle Protocol Buffer message objects
        if hasattr(obj, 'DESCRIPTOR') and hasattr(obj, 'SerializeToDict'):
            return obj.SerializeToDict()
        # Handle Protocol Buffer message objects (alternative method)
        if hasattr(obj, 'DESCRIPTOR') and hasattr(obj, 'ListFields'):
            result = {}
            for field, value in obj.ListFields():
                result[field.name] = value
            return result
        return super().default(obj)


class JSONEncoder(Encoder):

    def encode(self, msg: "StructuredMessage"):
        d = {**msg.kwargs, "msg": msg.message}
        return json.dumps(d, cls=DataclassJSONEncoder)


class PlainTextEncoder(Encoder):

    def encode(self, msg: "StructuredMessage"):
        extra = " ".join(f"\033[32m[{k}]={v}\033[0m" for k, v in msg.kwargs.items())
        return f"{msg.message} {extra}"


class StackdriverEncoder(Encoder):
    SEVERITY_MAP = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }
    DEFAULT_SEVERITY = "INFO"

    def encode(self, msg: "StructuredMessage") -> dict:
        severity = self.SEVERITY_MAP.get(
            str(msg.kwargs.get("level", "")).upper(), self.DEFAULT_SEVERITY
        )

        # Create a copy of kwargs to avoid modifying the original
        kwargs_copy = msg.kwargs.copy()
        # Remove 'level' from kwargs_copy if it exists, as it's handled separately
        if "level" in kwargs_copy:
            del kwargs_copy["level"]

        stackdriver_msg = {
            "severity": severity,
            "message": msg.message,
            **kwargs_copy,
        }
        return json.dumps(stackdriver_msg, cls=DataclassJSONEncoder)


# Modify encoder initialization based on environment variable
provider = os.getenv('LOGGING_PROVIDER', 'json').lower()
if provider == 'stackdriver':
    encoder: Encoder = StackdriverEncoder()
else:
    encoder: Encoder = JSONEncoder()

class StructuredMessage:
    message: str
    kwargs: dict

    def __init__(self, message, /, **kwargs):
        self.message = message
        self.kwargs = kwargs

    def __str__(self):
        return encoder.encode(self)

s_ = StructuredMessage
