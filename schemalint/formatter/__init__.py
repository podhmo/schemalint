import os.path
import logging
from schemalint.loader import Loader
from schemalint.errors import Error, ParseError, ResolutionError, ValidationError
from .detector import Detector


logger = logging.getLogger(__name__)


class ErrorFormatter:
    detector: Detector

    def __init__(self, filename: str, *, detector: Detector):
        self.filename = filename
        self.detector = detector

    def format(self, err: Error) -> str:
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

        return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"

    def format_resolution_error(self, err: ResolutionError) -> str:
        start_mark, end_mark = self.detector.detect_loadning_start_point(err)
        filename = os.path.relpath(start_mark.name, start=".")
        status = self.detector.detect_status(err.history[-1])
        msg = repr(err.inner)

        where = [os.path.relpath(name) for name in err.history]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        if self.detector.has_error_point(err):
            where[-1] = f"{where[-1]}:{err.inner.problem_mark.line+1}"
        return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"

    def format_validation_error(self, err: ValidationError) -> str:
        status = "ERROR"
        msg = f"{err.message} (validator={err.validator})"
        node = self.detector.store.lookup_node(err.instance)  # xxx

        start_mark, end_mark = node.start_mark, node.end_mark

        filename = os.path.relpath(start_mark.name, start=".")
        where = [os.path.relpath(filename)]
        where[0] = f"{where[0]}:{start_mark.line+1}"
        return f"status:{status}	cls:{err.__class__.__name__}	filename:{filename}	start:{start_mark.line+1}@{start_mark.column}	end:{end_mark.line+1}@{end_mark.column}	msg:{msg}	where:{where}"


def get_formatter(filename: str, *, loader: Loader) -> ErrorFormatter:
    detector = Detector(filename, store=loader.store)
    return ErrorFormatter(filename, detector=detector)
