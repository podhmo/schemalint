import typing as t
from dictknife import loading
from dictknife.langhelpers import reify

from .entity import ErrorEvent, Context
from .errors import MessageError
from .loader import get_loader, Loader
from .validator import get_validator, Validator


class Stream:  # todo: to protocol
    def __iter__(self) -> t.Iterable[ErrorEvent]:
        raise NotImplementedError("need")

    context: Context = None  # xxx:


class StreamFromLoader(Stream):
    def __init__(self, ctx: Context, *, loader: Loader) -> None:
        self.context = ctx
        self.loader = loader

        self._seen = set()
        ctx.filename = loader.filename  # xxx
        ctx.lookup = loader.store  # xxx

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
    s = StreamFromLoader(ctx, loader=loader)
    ctx.doc = s.doc  # xxx
    return s


class StreamWithMessages(Stream):
    def __init__(self, stream: StreamFromLoader, *, messages: t.List[str]) -> None:
        self._stream = stream
        self.messages = messages

    @property
    def context(self):
        return self._stream.context

    def __iter__(self) -> t.Iterable[ErrorEvent]:
        yield from self._stream
        for message in self.messages:
            yield ErrorEvent(
                error=MessageError(message), context=self.context, has_soft_error=True
            )


def append_messages(
    stream: StreamFromLoader, *, messages: t.List[str]
) -> StreamFromLoader:
    return StreamWithMessages(stream, messages=messages)


class StreamWithValidator(Stream):
    def __init__(self, stream: StreamFromLoader, *, validator: Validator) -> None:
        self._stream = stream
        self.validator = validator

    @property
    def context(self):
        return self._stream.context

    def __iter__(self) -> t.Iterable[ErrorEvent]:
        yield from self._stream
        for err in self.validator.iter_errors(self._stream.context.doc):
            yield ErrorEvent(context=self._stream.context, error=err)


def with_validator(s: StreamFromLoader, validator: Validator) -> StreamWithValidator:
    return StreamWithValidator(s, validator=validator)


def with_schema(
    s: StreamFromLoader, filepath: str, *, check_schema: bool
) -> StreamWithValidator:
    schema = loading.loadfile(filepath)
    validator = get_validator(schema, check_schema=check_schema)
    return with_validator(s, validator)
