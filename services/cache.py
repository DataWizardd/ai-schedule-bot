import time
from typing import Dict, Any, Tuple

class SuggestionCache:
    def __init__(self, ttl_sec: int = 600):
        self.ttl = ttl_sec
        self.store: Dict[Tuple[int,int], Tuple[float, Any]] = {}

    def put(self, chat_id: int, msg_id: int, payload: Any):
        self.store[(chat_id, msg_id)] = (time.time(), payload)

    def get(self, chat_id: int, msg_id: int):
        v = self.store.get((chat_id, msg_id))
        if not v: return None
        ts, payload = v
        if time.time() - ts > self.ttl:
            del self.store[(chat_id, msg_id)]
            return None
        return payload
