from __future__ import annotations

import hashlib

from .sending import *
from .errors import *
from .network import *
from .configbase import *
from .temporarymanager import *
from .fs import *
from .caching import *

def sha256(data: str):
    return hashlib.sha256(data.encode()).hexdigest()