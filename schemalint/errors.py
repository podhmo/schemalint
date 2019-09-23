import typing as t
import jsonschema

ValidationError = jsonschema.ValidationError  # noqa


class LintError(Exception):
    def __init__(
        self, inner: str, *, history: list, path: list = None, data: dict = None
    ):
        super().__init__(repr(inner))
        self.inner = inner
        self.history = history
        self.path = path
        self.data = data

    def __str__(self):
        return f"{self.__class__.__name__}: {self.inner}"


class ParseError(LintError):
    # usually, inner is MarkedYAMLError
    pass


class ResolutionError(LintError):
    # usually, inner is KeyError or FileNotFoundError
    pass


class MessageError(Exception):
    pass


Error = t.Union[LintError, ValidationError, MessageError]
