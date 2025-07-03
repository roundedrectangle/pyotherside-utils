from __future__ import annotations

import shutil
from pathlib import Path

from .network import DownloadManager

__ALL__ = ['TemporaryManager']

class TemporaryManager(DownloadManager):
    """HACK: StandardPaths.Temporary uses private-tmp (in other words /tmp is separated between apps in sailijail), so we manage our own temporary folder"""

    def __init__(self, cache: Path | str, proxy: str | None = None, user_agent: str | None = None):
        super().__init__(proxy, user_agent)
        self.temp = Path(cache) / 'temporary'
        self.clear()
        self.create()

    def save(self, url: str, filename: str):
        dest = self.temp / filename
        self.download_save(url, dest, False)
        return dest
    
    def open(self, filename: str, mode: str = 'w'):
        return open(self.temp / filename, mode)

    def save_contents(self, contents: str, filename: str):
        with self.open(filename, 'w') as f:
            f.write(contents)
            return Path(f.name)

    def clear(self):
        shutil.rmtree(self.temp, ignore_errors=True)
    
    def create(self):
        self.temp.mkdir(parents=True, exist_ok=True)
