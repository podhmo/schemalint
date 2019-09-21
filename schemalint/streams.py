from __future__ import annotations
import typing as t
from dataclasses import dataclass, field

from dictknife import loading
from dictknife.langhelpers import reify

from .errors import Error
from .loader import get_loader, Loader
from .validator import get_validator, Validator


@dataclass(frozen=True)
class ErrorEvent:
    error: Error  # xxx
    context: Context


@dataclass(unsafe_hash=False, frozen=False)
class Context:
    filename: str = ""
    doc: dict = field(default_factory=dict)
    loader: Loader = None  # xxx


class Stream:  # todo: to protocol
    def __iter__(self) -> t.Iterable[ErrorEvent]:
        raise NotImplementedError("need")

    context: Context = None  # xxx:


class StreamFromLoader(Stream):
    def __init__(self, ctx: Context, *, loader: Loader) -> None:
        self.context = ctx
        self.loader = loader

        self._seen = set()
        ctx.loader = loader  # xxx

    @reify
    def doc(self) -> dict:
        return self.loader.load()

    def __iter__(self) -> t.Iterable[ErrorEvent]:
        self.context.doc = self.doc
        for err in self.loader.errors:
            if err in self._seen:
                continue
            yield ErrorEvent(error=err, context=self.context)


def from_filename(filepath: str, ctx: t.Optional[Context] = None) -> StreamFromLoader:
    loader = get_loader(filepath)
    return from_loader(loader, ctx=ctx)


def from_loader(loader: Loader, *, ctx: t.Optional[Context] = None) -> StreamFromLoader:
    ctx = ctx or Context()
    return StreamFromLoader(ctx, loader=loader)


class StreamWithValidator(Stream):
    def __init__(self, stream: StreamFromLoader, *, validator: Validator) -> None:
        self._stream = stream
        self.validator = validator

    @property
    def context(self):
        self._stream.doc  # xxx:
        return self._stream.context

    def __iter__(self) -> t.Iterable[ErrorEvent]:
        yield from self._stream
        for err in self.validator.iter_errors(self._stream.doc):
            yield ErrorEvent(context=self._stream.context, error=err)


def with_validator(s: StreamFromLoader, validator: Validator) -> StreamWithValidator:
    return StreamWithValidator(s, validator=validator)


def with_schema(
    s: StreamFromLoader, filepath: str, *, check_schema: bool
) -> StreamWithValidator:
    schema = loading.loadfile(filepath)
    validator = get_validator(schema, check_schema=check_schema)
    return with_validator(s, validator)
