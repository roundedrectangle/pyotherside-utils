from pathlib import Path
from typing import Any
import json

from . import qsend, show_error

__ALL__ = ['ConfigBase']

class ConfigBase:
    """Pydantic reinvention"""
    _location: Path
    _name: str
    _data: None | Any = None
    _default: None | Any = None

    def show_error(self, name: str, save=False):
        show_error(f'config{"Save" if save else "Load"}{name}', self._name)

    @property
    def _path(self):
        return Path(self._location) / f'{self._name}.json'

    def __init__(self, location : str | Path):
        self._location = Path(location)
        try:
            self._location.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            show_error('configDirPermissions', self._name, self._location)
        if not hasattr(self, '_name'):
            self._name = 'config'
        if self._data is None:
            self.reset(save=False)
        self.load()
        if not self._path.is_file():
            self.save()

    def reset(self, save=True):
        self._data = self._default
        if save:
            self.save()

    def load(self):
        if not self._path.is_file():
            return
        try:
            with open(self._path) as f:
                data = f.read()
        except PermissionError:
            self.show_error('Permissions')
            return
        try:
            self._data = json.loads(data)
        except json.JSONDecodeError:
            self.show_error('JSON')
            self._data = self._default
        return True
    
    def save(self):
        qsend(str(self._data))
        try:
            with open(self._path, 'w') as f:
                f.write(json.dumps(self._data, separators=(',', ':')))
        except PermissionError:
            self.show_error('Permissions', True)
            return
        except FileNotFoundError:
            self.show_error('NotFound', True)
            return
        return True
    
    def reset_if(self, statement):
        if statement:
            self.reset()
        return statement