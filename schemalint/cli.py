import os.path
import subprocess
import logging
from schemalint.loader import get_scanner  # todo: rename
from schemalint.formatter import get_describer  # todo: rename

logger = logging.getLogger(__name__)


def run(filename: str):
    filename = os.path.abspath(filename)

    scanner = get_scanner(filename)
    doc = scanner.scan()
    print("----------------------------------------")
    subprocess.run(["cat", "-n", filename])
    # from dictknife import loading
    # loading.dumpfile(doc)

    if scanner.errors:
        describer = get_describer(filename, scanner=scanner)
        print("?", len(scanner.errors))
        for err in scanner.errors:
            print(describer.describe(err))


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
