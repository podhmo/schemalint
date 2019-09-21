from __future__ import annotations
import typing as t
import logging
from dataclasses import dataclass, field

from typing_extensions import Protocol

from .errors import Error

logger = logging.getLogger(__name__)


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


class NodeStore(Lookup):
    def __init__(self):
        self.cache = {}

    def add_node(self, name, node, r):
        logger.debug("add_node %s", name)
        if r is None:
            return r
        self.cache[id(r)] = node
        return r

    def lookup_node(self, data: object) -> object:
        return self.cache[id(data)]
