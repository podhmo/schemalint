from __future__ import annotations
import typing as t
from dataclasses import dataclass, field

from typing_extensions import Protocol

from .errors import Error


@dataclass(frozen=True)
class ErrorEvent:
    error: Error  # xxx
    context: Context


@dataclass(unsafe_hash=False, frozen=False)
class Context:
    filename: str = ""
    doc: dict = field(default_factory=dict)
    lookup: t.Optional[Lookup] = None


class Lookup(Protocol):
    def lookup_node(self, data: object) -> object:
        ...
