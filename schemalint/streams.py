from __future__ import annotations
import typing as t
from dataclasses import dataclass, field
from .loader.errors import LintError
from dictknife.langhelpers import reify


@dataclass(frozen=True)
class ErrorEvent:
    error: LintError  # xxx
    context: Context


@dataclass(unsafe_hash=False)
class Context:
    filename: str = ""
    doc: dict = field(default_factory=dict)


class StreamFromLoader:
    def __init__(self, ctx: Context, *, loader):
        self._ctx = ctx
        self._loader = loader
        self._seen = set()

    @reify
    def doc(self) -> dict:
        return self._loader.load()

    def __iter__(self) -> t.Iterable[ErrorEvent]:
        self._ctx.doc = self.doc
        for err in self._loader.errors:
            if err in self._seen:
                continue
            yield ErrorEvent(error=err, context=self._ctx)


def from_loader(loader, *, ctx: t.Optional[Context] = None):
    ctx = ctx or Context()
    return StreamFromLoader(ctx, loader=loader)
