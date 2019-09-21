import typing as t
import os.path
import logging

from yaml.error import Mark
from typing_extensions import TypedDict, Protocol

from schemalint.entity import ErrorEvent, Lookup
from schemalint.errors import ParseError, LintError, ResolutionError, ValidationError


logger = logging.getLogger(__name__)


class OutputDict(TypedDict):
    status: str
    errortype: str
    filename: str

    start: str
    end: str

    msg: str
    where: str


class Layout(Protocol):
    def layout(self, d: OutputDict) -> str:
        ...


class LTSVLayout(Layout):
    def layout(self, d: OutputDict) -> str:
        return "\t".join(f"{k}:{v}" for k, v in d.items())


class Detector:
    lookup: Lookup

    def __init__(self, filename: str, *, lookup: Lookup):
        self.filename = filename  # root file
        self.lookup = lookup

    def has_error_point(self, err: LintError):
        return getattr(err, "problem_mark", None) is not None

    def detect_status(self, filename):
        if self.filename == filename:
            return "ERROR"
        else:
            return "WARNING"

    def detect_loadning_start_point(self, err: LintError) -> (Mark, Mark):
        if err.data is None:
            return self.detect_error_point(err)
        map_node = self.lookup.lookup_node(err.data)
        knode, vnode = self.lookup_kvpair(map_node, err.path[-1])
        return knode.start_mark, vnode.end_mark

    def detect_error_point(self, err: LintError) -> Mark:
        mark = getattr(err.inner, "context_mark")
        import copy

        if mark is None:
            mark = getattr(err.inner, "problem_mark")
            mark.line -= 1  # xxx

        start_mark = copy.deepcopy(mark)
        start_mark.column = 0
        end_mark = copy.deepcopy(mark)
        end_mark.column = -1
        return (start_mark, end_mark)

    def lookup_kvpair(self, node, k):  # todo: rename
        for knode, vnode in node.value:
            if knode.value == k:
                return knode, vnode


class Formatter:
    detector: Detector
    layout: Layout

    def __init__(
        self, filename: str, *, detector: Detector, layout: t.Optional[Layout] = None
    ):
        self.filename = filename
        self.detector = detector
        self.layout = layout or LTSVLayout()

    def format(self, ev: ErrorEvent) -> str:
        err = ev.error
        if isinstance(err, ParseError):
            return self.format_parse_error(err)
        elif isinstance(err, ResolutionError):
            return self.format_resolution_error(err)
        elif isinstance(err, ValidationError):
            return self.format_validation_error(err)
        else:
            raise err

    def format_parse_error(self, err: ParseError) -> str:
        status = self.detector.detect_status(err.history[-1])
        if hasattr(err.inner, "problem"):
            msg = f"{err.inner.problem} ({err.inner.context})"
        else:
            msg = repr(err.inner)

        start_mark, end_mark = self.detector.detect_loadning_start_point(err)
        filename = os.path.relpath(start_mark.name, start=".")

        where = [os.path.relpath(name) for name in err.history]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        if self.detector.has_error_point(err):
            where[-1] = f"{where[-1]}:{err.inner.problem_mark.line+1}"

        return self.layout.layout(
            OutputDict(
                status=status,
                errortype=err.__class__.__name__,
                filename=filename,
                start=f"{start_mark.line+1}@{start_mark.column}",
                end=f"{end_mark.line+1}@{end_mark.column}",
                msg=msg,
                where=where,
            )
        )

    def format_resolution_error(self, err: ResolutionError) -> str:
        start_mark, end_mark = self.detector.detect_loadning_start_point(err)
        filename = os.path.relpath(start_mark.name, start=".")
        status = self.detector.detect_status(err.history[-1])
        msg = repr(err.inner)

        where = [os.path.relpath(name) for name in err.history]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        if self.detector.has_error_point(err):
            where[-1] = f"{where[-1]}:{err.inner.problem_mark.line+1}"

        return self.layout.layout(
            OutputDict(
                status=status,
                errortype=err.__class__.__name__,
                filename=filename,
                start=f"{start_mark.line+1}@{start_mark.column}",
                end=f"{end_mark.line+1}@{end_mark.column}",
                msg=msg,
                where=where,
            )
        )

    def format_validation_error(self, err: ValidationError) -> str:
        status = "ERROR"
        msg = f"{err.message} (validator={err.validator})"
        node = self.detector.lookup.lookup_node(err.instance)  # xxx

        start_mark, end_mark = node.start_mark, node.end_mark

        filename = os.path.relpath(start_mark.name, start=".")
        where = [os.path.relpath(filename)]
        where[0] = f"{where[0]}:{start_mark.line+1}"

        return self.layout.layout(
            OutputDict(
                status=status,
                errortype=err.__class__.__name__,
                filename=filename,
                start=f"{start_mark.line+1}@{start_mark.column}",
                end=f"{end_mark.line+1}@{end_mark.column}",
                msg=msg,
                where=where,
            )
        )


def get_formatter(filename: str, *, lookup: Lookup) -> Formatter:
    detector = Detector(filename, lookup=lookup)
    return Formatter(filename, detector=detector)
