from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable
import json

from pyotherside_utils.errors import ExceptionHandlingInfo

from . import qsend, show_error, exception_safe

__ALL__ = ['ConfigBase', 'JSONConfigBase']

class ConfigBase(ABC):
    _location: Path
    _name: str = 'config'
    _extension: str = 'json'
    _data: None | Any = None
    _default: None | Any = None
    _default_factory: None | Callable = None

    def get_error(self, name: str, save=False):
        return f'config{"Save" if save else "Load"}{name}', self._name

    def show_error(self, name: str, save=False):
        show_error(self.get_error(name, save))

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
        self._data = self._default_factory() if self._default_factory is not None else self._default
        if save:
            self.save()
    
    @abstractmethod
    def _load(self, data: str) -> tuple[bool, Any]:
        """When implementing a config backend, this method should return a tuple of the result as a boolean and the encoded data in data argument decoded."""
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
        state, data = self._load(data)
        if state:
            self._data = data
        else:
            self.reset()
        return state

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
    """Example configuration backend implementation. Parses objects as JSON."""

    _extension = 'json'

    def _load(self, data) -> tuple[bool, Any]:
        @exception_safe({json.JSONDecodeError: ExceptionHandlingInfo(*self.get_error('JSON'), return_on_exc=(False, None))})
        def wrapper():
            return True, json.loads(data)
        return wrapper()

    def _dump(self, data) -> tuple[bool, Any]:
        # if something is not JSON serializable (TypeError), it is probably a logic error, so we don't check it
        return True, json.dumps(data, separators=(',', ':'))