import hashlib

def sha256(data: str):
    return hashlib.sha256(data.encode()).hexdigest()