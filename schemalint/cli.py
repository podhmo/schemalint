import os.path
import subprocess
import logging
from schemalint.loader import get_loader  # todo: rename
from schemalint.formatter import get_formatter  # todo: rename

logger = logging.getLogger(__name__)


def run(filename: str):
    filename = os.path.abspath(filename)

    loader = get_loader(filename)
    doc = loader.load()
    print("----------------------------------------")
    subprocess.run(["cat", "-n", filename])
    # from dictknife import loading
    # loading.dumpfile(doc)

    if loader.errors:
        formatter = get_formatter(filename, loader=loader)
        print("?", len(loader.errors))
        for err in loader.errors:
            print(formatter.format(err))


def main(argv=None):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("filename")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)

    run(**vars(args))


if __name__ == "__main__":
    main()
