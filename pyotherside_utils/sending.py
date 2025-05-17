from datetime import datetime
from typing import TYPE_CHECKING

__ALL__ = [
    'qsend',
    'qml_date',
]

qsend = lambda *args: print(*args) # Fallback for testing
if not TYPE_CHECKING:
    try: from pyotherside import send as qsend
    except: pass

def qml_date(date: datetime):
    """Convert to UTC Unix timestamp using milliseconds"""
    return date.timestamp()*1000