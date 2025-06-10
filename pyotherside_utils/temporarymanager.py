from __future__ import annotations

import shutil
from pathlib import Path

from . import qsend, DownloadManager

__ALL__ = ['TemporaryManager']

class TemporaryManager(DownloadManager):
    """HACK: StandardPaths.Temporary uses private-tmp (in other words /tmp is separated between apps in sailijail), so we manage our own temporary folder"""

    def __init__(self, cache: Path | str, proxy: str | None = None, user_agent: str | None = None):
        super().__init__(proxy, user_agent)
        self.temp = Path(cache) / 'temporary'
        self.clear_temporary()
        self.recreate_temporary()

    def save_temporary(self, url: str, filename: Path | str):
        dest = self.temp / filename
        self.download_save(url, dest, False)
        return dest

    def clear_temporary(self):
        shutil.rmtree(self.temp, ignore_errors=True)
    
    def recreate_temporary(self):
        self.temp.mkdir(parents=True, exist_ok=True)
