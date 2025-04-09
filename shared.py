import json
from typing import Dict, Any, List


class LamportClock:
    def __init__(self):
        self.time = 0

    def increment(self) -> int:
        self.time += 1
        return self.time

    def update(self, received_time: int) -> int:
        self.time = max(self.time, received_time) + 1
        return self.time


def serialize(msg: Dict[str, Any]) -> bytes:
    """
    Convert a dictionary to JSON bytes with newline delimiter.
    """
    return (json.dumps(msg) + "\n").encode("utf-8")


def deserialize(data: bytes) -> Dict[str, Any]:
    """
    Safely decode a single JSON object from bytes.
    Only use if you're certain the message is one complete JSON.
    """
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"[!] JSON decode error: {e}")
        return {}


def deserialize_stream(stream: bytes) -> List[Dict[str, Any]]:
    """
    Decode a stream of newline-delimited JSON messages into a list of dicts.
    """
    messages = []
    try:
        lines = stream.decode("utf-8").splitlines()
        for line in lines:
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"[!] JSON line decode error: {e}")
    except Exception as e:
        print(f"[!] Stream decode error: {e}")
    return messages
