import logging
import yaml
from collections import ChainMap

from dictknife import DictWalker, Accessor
from dictknife.jsonknife.accessor import StackedAccessor, is_ref
from dictknife.langhelpers import make_dict
from dictknife.jsonknife import get_resolver

from schemalint.errors import ParseError, ResolutionError
from . import internal

logger = logging.getLogger(__name__)


class Loader:
    def __init__(self, resolver, *, store: internal.NodeStore):
        self.resolver = resolver
        self.accessor = StackedAccessor(resolver)
        self.accessing = Accessor()
        self.ref_walking = DictWalker([is_ref])
        self.errors = []
        self.store = store

    def load(self, doc=None, resolver=None):
        if not doc and doc is not None:
            return doc
        resolver = resolver or self.resolver
        try:
            doc = doc or resolver.doc
        except internal.MarkedYAMLError as e:
            if e.problem_mark is not None:
                self.errors.append(ParseError(e, history=[resolver.filename]))
            if doc is None:
                doc = {}
        doc, _ = self._load(doc, resolver=resolver, seen={})
        return doc

    def _load(self, doc, *, resolver, seen: dict):
        if "$ref" in doc:
            original = self.accessor.access(doc["$ref"])
            new_doc, _ = self._load(
                original, resolver=self.accessor.resolver, seen=seen
            )
            return new_doc, self.accessor.pop_stack()
        else:
            for path, sd in self.ref_walking.iterate(doc):
                try:
                    uid = id(sd)
                    if uid in seen:
                        continue

                    seen[uid] = sd
                    new_sd, sresolver = self._load(sd, resolver=resolver, seen=seen)
                    if resolver.filename != sresolver.filename:
                        container = self.accessing.access(doc, path[:-1])
                        if not hasattr(container, "parents"):
                            container = ChainMap(make_dict(), container)
                            container.update(new_sd)
                        self.accessing.assign(doc, path[:-1], container)
                except FileNotFoundError as e:
                    self.errors.append(
                        ResolutionError(
                            e,
                            path=path[:],
                            data=sd,
                            history=[r.filename for r in self.accessor.stack[:-1]],
                        )
                    )
                except KeyError as e:
                    self.errors.append(
                        ResolutionError(
                            e,
                            path=path[:],
                            data=sd,
                            history=[r.filename for r in self.accessor.stack],
                        )
                    )
                except internal.MarkedYAMLError as e:
                    if e.problem_mark is not None:
                        self.errors.append(
                            ParseError(
                                e,
                                path=path[:],
                                data=sd,
                                history=[r.filename for r in self.accessor.stack],
                            )
                        )
            return doc, resolver


class _Adapter:
    def __init__(self, yamlloader_factory):
        self.yamlloader_factory = yamlloader_factory

    def loadfile(self, filename, *, format=None):
        with open(filename) as rf:
            return yaml.load(rf, Loader=self.yamlloader_factory)


def get_loader(filename: str) -> Loader:
    store = internal.NodeStore()
    yaml_loader_factory = internal.YAMLLoaderFactory(internal.YAMLLoader, store=store)

    resolver = get_resolver(filename, loader=_Adapter(yaml_loader_factory))
    return Loader(resolver, store=store)
