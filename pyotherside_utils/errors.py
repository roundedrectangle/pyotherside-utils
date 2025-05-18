from dataclasses import dataclass
from typing import Any, Callable, TypeVar
import json
import functools
import traceback as tb
from enum import Enum

from . import qsend

T = TypeVar("T", str, Callable[[Exception], str])

__ALL__ = [
    'DataFromException',
    'ensure_data_from_exc',
    'show_error',
    'ExceptionHandlingInfo',
    'exception_safe',
    'json_safe',
]

class DataFromException(Enum):
    exception_name = 0
    str_exception = 1
    traceback = 2

    def to_data(self, e):
        if self == DataFromException.exception_name:
            return type(e).__name__
        if self == DataFromException.str_exception:
            return str(e)
        if self == DataFromException.traceback:
            return tb.format_exc()
        return ''

def ensure_data_from_exc(data: T | DataFromException | Any, e: Exception, check_callable = False) -> T | str:
    if isinstance(data, DataFromException):
        return data.to_data(e)
    if check_callable and callable(data):
        return str(data(e))
    return data

def show_error(name, info: Any = '', other = None):
    qsend('error', name, str(info), other)

@dataclass
class ExceptionHandlingInfo:
    name: str
    info: DataFromException | str | Callable[[Exception], str] = ''
    other: DataFromException | str | Callable[[Exception], str] = ''
    prepend_info: str = ''
    return_on_exc: DataFromException | Any = None

    def show(self, e):
        show_error(
            self.name,
            self.prepend_info + ensure_data_from_exc(self.info, e, check_callable=True),
            ensure_data_from_exc(self.other, e, check_callable=True)
        )

# def exception_safe(exc: type[Exception] | tuple[type[Exception]], name = None, other: DataFromException | Any = None, return_on_exc: DataFromException | Any = None):
def exception_safe(exceptions: dict[type[Exception], ExceptionHandlingInfo | str]):
    def wrapper(f):
        @functools.wraps(f)
        def new_f(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except tuple(exceptions.keys()) as e:
                exception = next((x for x in exceptions.keys() if isinstance(e, x)), None)
                if exception is not None:
                    handler = exceptions[exception]
                    if isinstance(handler, ExceptionHandlingInfo):
                        handler.show(e)
                        return handler.return_on_exc
                    else:
                        show_error(handler)
                else:
                    # Should never happen, since the dict always has the raised exception type in its keys
                    show_error('unknown', tb.format_exc())

        return new_f
    return wrapper

json_safe = lambda name='json': exception_safe({json.JSONDecodeError: ExceptionHandlingInfo(name, DataFromException.str_exception)})