from __future__ import annotations

import hashlib

from .sending import *
from .errors import *
from .network import *
from .configbase import *

def sha256(data: str):
    return hashlib.sha256(data.encode()).hexdigest()