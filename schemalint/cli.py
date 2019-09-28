import typing as t
import sys
import os.path
import logging
from schemalint import streams
from schemalint.entity import LoggerWithCollectMessage
from schemalint.formatter import get_formatter, OutputType
from schemalint import guess

logger = logging.getLogger(__name__)


def run(
    filename: str,
    *,
    schema: t.Optional[str] = None,
    guess_schema: bool,
    always_success: bool,
    output: OutputType,
) -> int:
    filepath = os.path.abspath(filename)
    s = streams.from_filename(filepath)

    if guess_schema:
        wlogger = LoggerWithCollectMessage(logger, {})
        schema = guess.guess_schema(
            ".schemalint.py", current=os.path.dirname(filename), logger=wlogger
        )
        s = streams.append_messages(s, messages=wlogger.messages)

    if schema is not None:
        schemapath = os.path.abspath(schema)
        s = streams.with_schema(s, schemapath, check_schema=True)

    formatter = get_formatter(filepath, lookup=s.context.lookup, output_type=output)

    success = True
    for ev in s:
        if not always_success and not ev.error.is_soft:
            success = False
        print(formatter.format(ev))
    return 0 if success else 1


def main(argv=None, *, run=run):
    import argparse

    parser = argparse.ArgumentParser(description=None)
    parser.print_usage = parser.print_help
    parser.add_argument("filename")
    parser.add_argument(
        "--logging", choices=list(logging._nameToLevel.keys()), default="INFO"
    )
    parser.add_argument("-s", "--schema")
    parser.add_argument(
        "-g",
        "--guess-schema",
        action="store_true",
        help="finding schema file via .schemalint.py",
    )
    parser.add_argument("-o", "--output", choices=["ltsv", "json"], default="ltsv")
    parser.add_argument("--always-success", action="store_true")

    args = parser.parse_args(argv)
    params = vars(args)

    logging.basicConfig(level=params.pop("logging"))
    try:
        sys.exit(run(**params))
    except Exception as e:
        if not args.always_success:
            raise
        formatter = get_formatter(args.filename, lookup=None, output_type=args.output)
        print(formatter.format_message_error(e, context=None))
        sys.exit(1)


if __name__ == "__main__":
    main()
