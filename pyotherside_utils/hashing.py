from functools import lru_cache
import hashlib

@lru_cache()
def sha256(data: str):
    return hashlib.sha256(data.encode()).hexdigest()