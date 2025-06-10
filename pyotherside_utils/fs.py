from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta, timezone
from itertools import islice

__ALL__ = [
    'update_required',
    'find_file',
]

def update_required(path: Path, minimum_time: timedelta):
    """Returns if the file at `path` was modified more or `minimum_time` ago."""
    mod = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    diff = now-mod
    return diff >= minimum_time

def find_file(path: Path | str, name: str, extension: str | None = None, default_extension='png'):
    """Finds file `name`.`extension` at `path`. If extension is None, then search for latest file with any extension.
    
    If not found, return the file with `default_extension` extension."""
    path = Path(path)
    if extension is None:# and isinstance(cache, Path):
        for f in sorted(path.glob(f'{name}.*'), key=lambda p: Path.stat(p).st_mtime):
            if not f.is_dir():
                return f
        extension = default_extension
    return path / f"{name}.{extension}"

def find_extracted_contents(path: Path | str):
    path = Path(path)
    while True:
        if len(list(islice(path.iterdir(), 2))) != 1 or path.is_file():
            break
        path = next(path.iterdir())
    return path

find_contents = find_extracted_contents # deprecated FIXME: remove this when i'll work on Utilities or whatever uses this

#AUTOINCREMENTED_FILE_PATH_RE = re.compile(r'^.* \([1-9][0-9]*\)$')
def autoincremented_file_path(path: Path | str):
    path = Path(path)
    try:
        i = 2
        if path.exists():
            path = path.with_stem(f'{path.stem} (2)')
        i += 1 # So if while loop is entered it will properly update path to be 3 instead of 2 and substract i-1 length without doing this 2 times
        while path.exists():
            path = path.with_stem(path.stem[:-(3 + len(str(i-1)))] + f' ({i})')
            i += 1
    except (FileNotFoundError, PermissionError):
        pass
    return path