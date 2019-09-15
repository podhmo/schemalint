import typing as t
import os.path
import subprocess
import logging
from dictknife import loading

from schemalint.loader import get_loader  # todo: rename
from schemalint.formatter import get_formatter  # todo: rename
from schemalint.validator import get_validator

logger = logging.getLogger(__name__)


def run(filename: str, *, schema: t.Optional[str] = None):
    filepath = os.path.abspath(filename)

    loader = get_loader(filepath)
    doc = loader.load()
    print("----------------------------------------")
    subprocess.run(["cat", "-n", filepath])
    # from dictknife import loading
    # loading.dumpfile(doc)

    if loader.errors:
        formatter = get_formatter(filepath, loader=loader)
        print("?", len(loader.errors))
        for err in loader.errors:
            print(formatter.format(err))

    if schema is None:
        return

    schemapath = os.path.abspath(schema)
    schema = loading.loadfile(schemapath)  # overwrite
    validator = get_validator(schema, check_schema=True)

    errors = list(validator.iter_errors(doc))
    print("?", len(errors))
    for e in errors:
        # print("path", e.path)
        # print("message", e.message)
        # print("instance", e.instance)
        # print(store.lookup_node(e.instance))
        # print("----------------------------------------")
        print(describe(loader.store, e))


import jsonschema
from schemalint.loader.internal import NodeStore


def describe(store: NodeStore, err: jsonschema.ValidationError) -> str:
    status = "ERROR"
    msg = f"{err.message} (validator={err.validator})"
    node = store.lookup_node(err.instance)

    start_mark, end_mark = node.start_mark, node.end_mark

    filename = os.path.relpath(start_mark.name, start=".")
    where = [os.path.relpath(filename)]
    where[0] = f"{where[0]}:{start_mark.line+1}"
    return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("filename")
    parser.add_argument("-s", "--schema")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    run(**vars(args))


if __name__ == "__main__":
    main()
