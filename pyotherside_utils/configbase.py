from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any
import json

from . import qsend, show_error

__ALL__ = ['ConfigBase', 'JSONConfigBase']

class ConfigBase(ABC):
    _location: Path
    _name: str = 'config'
    _extension: str = 'json'
    _data: None | Any = None
    _default: None | Any = None

    def show_error(self, name: str, save=False):
        show_error(f'config{"Save" if save else "Load"}{name}', self._name)

    @property
    def _path(self):
        return Path(self._location) / f'{self._name}.{self._extension}'

    def __init__(self, location: str | Path):
        self._location = Path(location)
        try:
            self._location.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            show_error('configDirPermissions', self._name, self._location)
        if self._data is None:
            self.reset(save=False)
        self.load()
        if not self._path.is_file():
            self.save()

    def reset(self, save=True):
        self._data = self._default
        if save:
            self.save()
    
    @abstractmethod
    def _load(self, data: str) -> bool:
        """When implementing a config backend, this method should save the data in data argument to self._data in decoded format."""
        ...

    @abstractmethod
    def _dump(self, data: Any) -> tuple[bool, str]:
        """When implementing a config backend, this method should return a tuple of the result as a boolean and the data in data argument dumped as a string."""
        ...

    def load(self):
        if not self._path.is_file():
            return
        try:
            with open(self._path) as f:
                data = f.read()
        except PermissionError:
            self.show_error('Permissions')
            return
        return self._load(data)

    def save(self):
        state, data = self._dump(self._data)
        if not state:
            return state
        try:
            with open(self._path, 'w') as f:
                f.write(data)
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

class JSONConfigBase(ConfigBase):
    _extension = 'json'

    def _load(self, data):
        try:
            self._data = json.loads(data)
        except json.JSONDecodeError:
            self.show_error('JSON')
            return False
        return True

    def _dump(self, data):
        # if something is not JSON serializable (TypeError), it is probably a logic error, so we don't check it
        return True, json.dumps(self._data, separators=(',', ':'))