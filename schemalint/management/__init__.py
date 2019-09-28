import typing as t
import logging
import os.path
import importlib.resources as resources

from dictknife import loading
from magicalimport import import_module

from schemalint.entity import Logger

logger = logging.getLogger(__name__)


def resolve(
    filepath: t.Optional[str] = None,
    *,
    schema: t.Optional[str] = None,
    package: str = "schemalint.management.resources",
    filename: str = "root.yaml",
    resource: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Optional[str]:
    if schema is not None:
        return schema
    if resource is not None:
        resource = _resolve_resource(package, filename=filename)
    return _resolve_path(filepath, resource)


def _resolve_resource(
    package: str, *, filename: t.Optional[str], support_extensions=(".yaml", ".yml")
) -> dict:
    for fname in resources.contents(package):
        if not os.path.splitext(fname)[1].endswith(support_extensions):
            continue

    with resources.open_text(package, fname) as rf:
        return loading.load(rf)


def _resolve_path(path: str, resource: t.Dict[str, t.Any]) -> t.Optional[str]:
    return


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
        logger.info(
            "not found, in %s, schema or get_schema() is not found, or return None",
            filepath,
        )
        return None
    except ModuleNotFoundError as e:
        logger.info("not found (%r)", e.__class__.__name__)
        return None
