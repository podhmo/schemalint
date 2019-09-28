import typing as t
import os.path
import logging

from .entity import Logger
from . import management

logger = logging.getLogger(__name__)


def _find_init_file(
    filename: str, *, current: t.Optional[str] = None
) -> t.Optional[str]:
    def iter_parents(filename, current=None):
        current = os.path.normpath(os.path.abspath(current or os.getcwd()))
        while True:
            yield os.path.join(current, filename)
            if current == "/":
                break
            current, dropped = os.path.split(current)

    for path in iter_parents(filename, current):
        logger.debug("check: %s", path)
        if os.path.exists(path):
            return path
    return None


def guess_schema(
    filename: str, *, current: t.Optional[str] = None, logger: Logger = logger
) -> t.Optional[str]:
    filepath = _find_init_file(".schemalint.py", current=current)
    if filepath is None:
        logger.info(".schemalint.py is not found")
        return None
    return management.get_schema(filepath, logger=logger)
