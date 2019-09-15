import os.path
import logging
from yaml.error import Mark

from schemalint.loader.internal import NodeStore  # todo: move
from schemalint.loader.errors import (
    LintError,
    ParseError,
    ResolutionError,
)  # todo: move
from schemalint.loader import DataScanner

logger = logging.getLogger(__name__)


class Detector:
    def __init__(self, filename: str, *, store: NodeStore):
        self.filename = filename  # root file
        self.store = store

    def has_error_point(self, err: LintError):
        return getattr(err, "problem_mark", None) is not None

    def detect_status(self, filename):
        if self.filename == filename:
            return "ERROR"
        else:
            return "WARNING"

    def detect_scanning_start_point(self, err: LintError) -> (Mark, Mark):
        if err.data is None:
            return self.detect_error_point(err)
        map_node = self.store.lookup_node(err.data)
        knode, vnode = self.lookup_kvpair(map_node, err.path[-1])
        return knode.start_mark, vnode.end_mark

    def detect_error_point(self, err: LintError) -> Mark:
        mark = getattr(err.inner, "context_mark")
        import copy

        start_mark = copy.deepcopy(mark)
        start_mark.column = 0
        end_mark = copy.deepcopy(mark)
        end_mark.column = -1
        return (start_mark, end_mark)

    def lookup_kvpair(self, node, k):  # todo: rename
        for knode, vnode in node.value:
            if knode.value == k:
                return knode, vnode


class Describer:
    def __init__(self, filename: str, *, store: NodeStore):
        self.filename = filename
        self.store = store
        self.detector = Detector(filename, store=store)

    def describe(self, err: LintError) -> str:
        if isinstance(err, ParseError):
            return self.describe_parse_error(err)
        elif isinstance(err, ResolutionError):
            return self.describe_resolution_error(err)
        else:
            raise err

    def describe_parse_error(self, err: ParseError) -> str:
        status = self.detector.detect_status(err.history[-1])
        if hasattr(err.inner, "problem"):
            msg = f"{err.inner.problem} ({err.inner.context})"
        else:
            msg = repr(err.inner)

        start_mark, end_mark = self.detector.detect_scanning_start_point(err)
        filename = os.path.relpath(start_mark.name, start=".")

        where = [os.path.relpath(name) for name in err.history]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        if self.detector.has_error_point(err):
            where[-1] = f"{where[-1]}:{err.inner.problem_mark.line+1}"

        return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"

    def describe_resolution_error(self, err: ResolutionError) -> str:
        start_mark, end_mark = self.detector.detect_scanning_start_point(err)
        filename = os.path.relpath(start_mark.name, start=".")
        status = self.detector.detect_status(err.history[-1])
        msg = repr(err.inner)

        where = [os.path.relpath(name) for name in err.history]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        if self.detector.has_error_point(err):
            where[-1] = f"{where[-1]}:{err.inner.problem_mark.line+1}"
        return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"


def get_describer(filename: str, *, scanner: DataScanner) -> Describer:
    return Describer(filename, store=scanner.store)
