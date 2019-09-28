import typing as t
import logging
import os.path
from schemalint.entity import Logger
from magicalimport import import_module

logger = logging.getLogger(__name__)


def resolve(path: t.Optional[str]) -> t.Optional[str]:
    return path


get_schema_function_type = t.Callable[[t.Optional[str]], t.Optional[str]]


def _get_schema(filepath: str, *, logger: Logger = logger) -> t.Optional[str]:
    m = import_module(filepath)
    for name in ["schema", "get_schema"]:
        # t.Optional[get_schema_function_type, t.Union[t.Optional[str]]]
        get_schema = getattr(m, name, None)
        if get_schema is None:
            continue

        schema = get_schema(filepath) if callable(get_schema) else get_schema
        if schema is None:
            continue

        return os.path.normpath(os.path.join(os.path.dirname(filepath), schema))
    return None


def get_schema(filepath: str, *, logger: Logger = logger) -> t.Optional[str]:
    try:
        schema = _get_schema(filepath, logger=logger)
        if schema is not None:
            return schema
        logger.info("not found, %s:schema or get_schema()", filepath)
        return None
    except ModuleNotFoundError as e:
        logger.info(
            "not found, %s:schema or get_schema() (%r)", filepath, e.__class__.__name__
        )
        return None
    except Exception as e:
        logger.warning("unexpected error %r", e)
        return None
