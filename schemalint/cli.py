import typing as t
import os.path
import subprocess
import logging
from schemalint import streams
from schemalint.formatter import get_formatter  # todo: rename


logger = logging.getLogger(__name__)


def run(filename: str, *, schema: t.Optional[str] = None):
    filepath = os.path.abspath(filename)
    s = streams.from_filename(filepath)

    if schema is not None:
        schemapath = os.path.abspath(schema)
        s = streams.with_schema(s, schemapath, check_schema=True)

    formatter = get_formatter(filepath, lookup=s.context.lookup)
    for ev in s:
        print(formatter.format(ev))

    print("----------------------------------------")
    subprocess.run(["cat", "-n", filepath])


def main(argv=None, *, run=run):
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
