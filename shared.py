import json
from typing import Dict, Any, List

class LamportClock:
    """
    Implements a simple Lamport logical clock for event ordering across distributed systems.
    """
    def __init__(self):
        self.time = 0

    def increment(self) -> int:
        """
        Increment the clock on a local event.
        """
        self.time += 1
        return self.time

    def update(self, received_time: int) -> int:
        """
        Update the clock based on received timestamp.
        Takes the maximum of current and received, then increments.
        """
        self.time = max(self.time, received_time) + 1
        return self.time

def serialize(msg: Dict[str, Any]) -> bytes:
    """
    Serialize a dictionary into JSON bytes, adding a newline delimiter for stream-safety.
    
    Args:
        msg: A dictionary to serialize.
    
    Returns:
        JSON-encoded bytes ending with a newline.
    """
    try:
        return (json.dumps(msg) + "\n").encode("utf-8")
    except Exception as e:
        print(f"[!] Serialization error: {e}")
        return b''

def deserialize(data: bytes) -> Dict[str, Any]:
    """
    Deserialize a complete JSON object from bytes.
    
    Only use if you're sure the data contains exactly one JSON object.

    Args:
        data: Byte stream of a JSON object.
    
    Returns:
        Decoded dictionary or an empty dict if decoding fails.
    """
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        print(f"[!] JSON decode error: {e}")
        return {}
    except Exception as e:
        print(f"[!] General deserialize error: {e}")
        return {}

def deserialize_stream(stream: bytes) -> List[Dict[str, Any]]:
    """
    Deserialize a stream of newline-delimited JSON objects.
    
    Args:
        stream: Bytes containing multiple newline-separated JSON messages.
    
    Returns:
        List of decoded dictionaries.
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
