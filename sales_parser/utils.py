import json
import sys
from datetime import datetime


def print_log(message: str):
    print("[LOG]", message, file=sys.stderr)


def print_error(message: str):
    print("[ERROR]", message, file=sys.stderr)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):  # type: ignore
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        elif hasattr(obj, "__dict__"):  # type: ignore
            return obj.__dict__  # type: ignore
        return super().default(obj)
