import typing as t
import sys
import subprocess
import json
from collections import defaultdict

from handofcats import as_command


def execute_schemalint(filename: str, *, schema: str) -> t.Iterable[t.Dict[str, t.Any]]:
    cmd = [
        sys.executable,
        "-m",
        "schemalint",
        "-s",
        schema,
        "-o",
        "json",
        filename,
        "--always-success",
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)

    for line in p.stdout.strip().split("\n"):
        yield json.loads(line)


def execute_cat(filename: str) -> t.Iterable[t.Tuple[int, str]]:
    try:
        with open(filename) as rf:
            for i, line in enumerate(rf, 1):
                yield i, line.rstrip()
    except FileNotFoundError as e:
        print(e)


@as_command
def run(filename: str, *, s: str) -> None:
    warn_dict = defaultdict(list)
    id_map = defaultdict(lambda: f"#{len(id_map)}")

    for d in execute_schemalint(filename, schema=s):
        uid = id_map[id(d)]
        d["uid"] = uid
        print(uid, d["status"], d["errortype"], d["message"])
        warn_dict[d["start"]["line"]].append(d)

    print("-")
    for i, line in execute_cat(filename):
        if i in warn_dict:
            print(f"{uid:s} > {i:02d}:{line}")
        else:
            print(f"{' ' * 5}{i:02d}:{line}")
