import typing as t
import logging
import os.path
import importlib_resources

from typing_extensions import TypedDict
from dictknife import loading
from magicalimport import import_module

from schemalint.entity import Logger

logger = logging.getLogger(__name__)


def resolve(
    filepath: t.Optional[str] = None,
    *,
    schema: t.Optional[str] = None,
    package: str = "schemalint.management.resources",
    resource_name: str = "root.yaml",
    resource: t.Optional[t.Dict[str, t.Any]] = None,
) -> t.Union[None, str, dict]:
    if schema is not None:
        return schema
    if resource is None:
        resource = _resolve_resource(package, name=resource_name)
    return _resolve_path(filepath, resource)


def _resolve_resource(
    package: str, *, name: t.Optional[str], support_extensions=(".yaml", ".yml")
) -> dict:
    logger.info("resolve resource, find resource from %s", package)
    for fname in importlib_resources.contents(package):
        if not os.path.splitext(fname)[1].endswith(support_extensions):
            continue
        name = fname
        break
    logger.info("resolve resource, load data from %s", name)
    with importlib_resources.open_text(package, name) as rf:
        return loading.load(rf)


class ResourceDict(TypedDict, total=False):
    name: str
    url: str  # url.format(version=version)
    version: t.Optional[t.List[t.Union[str, int, float]]]
    alias: t.Optional[t.Dict[str, str]]


def _resolve_path(path: str, resource: t.Dict[str, t.Any]) -> t.Optional[str]:
    # todo: logging
    filepath = os.path.basename(path)
    data = resource.get(filepath)
    if data is None:
        return None
    definition = ResourceDict(name=filepath, **data)

    url = definition["url"]
    if "{" not in url:
        return url

    # loadata (TODO:shared loaded data)
    from dictknife import loading
    from dictknife.jsonknife import access_by_json_pointer

    data = loading.loadfile(filepath)
    try:
        logger.info(
            "resolve schema, get version via %r, from %s",
            definition["get-version"],
            filepath,
        )
        version = str(access_by_json_pointer(data, definition["get-version"]))
    except KeyError:
        logger.info(
            "resolve schema, version is not found, guess latest version from %s",
            definition.get("version"),
        )
        version = definition["version"][0]
    logger.info("resolve schema, got version %s", version)

    if "alias" in definition:
        old_version, version = version, definition["alias"].get(version, version)
        logger.info("resolve schema, use alias %s -> %s", old_version, version)

    return url.format(version=version)


def get_schema(filepath: str, *, codepath: str) -> t.Union[str, dict, None]:
    m = import_module(codepath, cwd=True)
    for name in ["schema", "get_schema"]:
        # t.Optional[get_schema_fn_type, t.Union[t.Optional[str]]]
        get_schema_fn = getattr(m, name, None)
        if get_schema_fn is None:
            continue

        schema = get_schema_fn(filepath) if callable(get_schema_fn) else get_schema_fn
        if schema is None:
            continue
        if isinstance(schema, str) and not schema.startswith(("https://", "http:")):
            return os.path.normpath(os.path.join(os.path.dirname(codepath), schema))
        return schema
    return None
