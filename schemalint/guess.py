import typing as t
import os.path
import logging

from magicalimport import import_module

from .entity import Logger

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

    try:
        m = import_module(filepath)
        for name in ["schema", "get_schema"]:
            get_schema = getattr(m, name, None)
            if get_schema is None:
                continue

            schema = get_schema(filepath) if callable(get_schema) else get_schema
            if schema is None:
                continue

            return os.path.normpath(os.path.join(os.path.dirname(filepath), schema))
    except ModuleNotFoundError as e:
        logger.info(
            "not found, %s:schema or get_schema() (%r)", filepath, e.__class__.__name__
        )
        return None
    except Exception as e:
        logger.warning("unexpected error %r", e)
        return None
    logger.info("not found, %s:schema or get_schema()", filepath)
    return None
