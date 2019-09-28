import typing as t
import os.path
import logging

from .entity import Logger
from . import management

pkglogger = logger = logging.getLogger(__name__)


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
        logger.debug("check %s", path)
        if os.path.exists(path):
            return path
    return None


def guess_schema(
    filepath: str,
    *,
    code: str,
    current: t.Optional[str] = None,
    logger: Logger = logger
) -> t.Union[None, str, dict]:
    pkglogger.info("guess schema, find python script %s", code)
    codepath = _find_init_file(code, current=current)
    if codepath is None:
        logger.info("guess schema, %s is not found, for %s", code, filepath)
        return None
    pkglogger.info("guess schema, found python script %s", os.path.relpath(codepath))
    schema = get_schema(filepath, codepath=codepath, logger=logger)
    if isinstance(schema, str):
        pkglogger.info("guess schema, guessed %s", os.path.relpath(schema))
    return schema


def get_schema(
    filepath: str, *, codepath: str, logger: Logger = logger
) -> t.Union[str, dict, None]:
    # filepath is the path of target yaml file
    # codepath is the path of python script to resolve validation schema
    try:
        schema = management.get_schema(filepath, codepath=codepath)
        if schema is not None:
            return schema

        logger.warning(
            "for %s, not found, in %s, schema or get_schema() is not found, or return None",
            filepath,
            codepath,
        )
        return None
    except ModuleNotFoundError as e:
        logger.warning(
            "for %s, %s is not found (%r)", filepath, codepath, e.__class__.__name__
        )
        return None
