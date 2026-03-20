from typing import Dict, Optional
import asyncio
from datetime import datetime, timedelta

class ManualCache:
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.ttl = ttl_seconds
        self._lock = asyncio.Lock()
    
    async def get(self, key: str):
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if datetime.now() < entry["expiry"]:
                    print(f"Cache HIT for {key}")
                    return entry["value"]
                else:
                    print(f"Cache Expired for {key}")
                    del self.cache[key]
            print(f"Cache MISS for {key}")
            return None
    
    async def set(self, key: str, value):
        async with self._lock:
            self.cache[key] = {
                "value": value,
                "expiry": datetime.now() + timedelta(seconds=self.ttl)
            }
            print(f"Cache SET for {key}, expires in {self.ttl} seconds")
    
    async def evict(self, key: str):
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                print(f"Cache EVICTED {key}")
    
    def get_stats(self):
        return {
            "size": len(self.cache),
            "keys": list(self.cache.keys())
        }