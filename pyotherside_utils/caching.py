from __future__ import annotations

"""Cache operations"""

from pathlib import Path
from datetime import timedelta
from typing import Iterable, Union, Optional

from . import qsend, show_error
from .network import DownloadManager
from .fs import update_required

DefaultUpdatePeriodMapping = (
    None, # Never
    timedelta(), # On app restart
    timedelta(hours=1),
    timedelta(1),
    timedelta(weeks=1),
    timedelta(30),
    timedelta(182.5), # half-yearly
    timedelta(365),
)
"Maps QML cache period slider system to timedelta objects. On app restart is timedelta(0), Never is None."

def convert_to_timedelta(data: timedelta | int | None, mapping=DefaultUpdatePeriodMapping):
    try:
        if isinstance(data, int):
            return mapping[data]
        else: return data # Already converted
    except:
        show_error('cacheTimedelta', f'{type(data)}: {data}')

class CacherBase(DownloadManager):
    """Implements file modification date check logic."""

    @property
    def update_period(self):
        return self._update_period

    @update_period.setter
    def update_period(self, value: timedelta | int | None): # pyright: ignore[reportPropertyTypeMismatch]
        self._update_period = convert_to_timedelta(value, self.update_period_mapping)

    def __init__(
        self,
        update_period: timedelta | int | None,
        update_period_mapping: Iterable[timedelta | None] = DefaultUpdatePeriodMapping,
        proxy: str | None = None,
        user_agent: str | None = None,
    ):
        super().__init__(proxy, user_agent)

        self._update_period = None
        self.update_period_mapping = update_period_mapping
        self.update_period = update_period

    def update_required(self, path: Path):
        if not path.exists() or self.update_period == timedelta(0):
            return True
        if self.update_period == None:
            return False
        return update_required(path, self.update_period)