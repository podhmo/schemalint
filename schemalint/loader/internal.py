import typing as t
import logging
import yaml.loader as yamlloader
from yaml.error import MarkedYAMLError  # noqa:
from dictknife.langhelpers import reify

logger = logging.getLogger(__name__)


class NodeStore:
    def __init__(self):
        self.cache = {}

    def add_node(self, name, node, r):
        logger.debug("add_node %s", name)
        if r is None:
            return r
        self.cache[id(r)] = node
        return r

    def lookup_node(self, data):
        return self.cache[id(data)]


class Constructor(yamlloader.SafeConstructor):
    @reify
    def store(self):
        return NodeStore()

    def construct_object(self, node, deep=False):
        r = super().construct_object(node, deep=deep)
        self.store.add_node("construct_object", node, r)
        return r

    def construct_sequence(self, node, deep=False):
        r = super().construct_sequence(node, deep=deep)
        self.store.add_node("construct_sequence", node, r)
        return r

    def construct_mapping(self, node, deep=False):
        r = super().construct_mapping(node, deep=deep)
        self.store.add_node("construct_mapping", node, r)
        return r


# copie from pyyaml
class YAMLLoader(
    yamlloader.Reader,
    yamlloader.Scanner,
    yamlloader.Parser,
    yamlloader.Composer,
    Constructor,
    yamlloader.Resolver,
):
    def __init__(self, stream):
        yamlloader.Reader.__init__(self, stream)
        yamlloader.Scanner.__init__(self)
        yamlloader.Parser.__init__(self)
        yamlloader.Composer.__init__(self)
        Constructor.__init__(self)
        yamlloader.Resolver.__init__(self)


class YAMLLoaderFactory:
    def __init__(
        self,
        loader_class: t.Callable[[t.IO], YAMLLoader],
        *,
        store: t.Optional[NodeStore] = None
    ):
        self.loader_class = loader_class
        self.store = store or NodeStore()

    def __call__(self, rf: t.IO) -> YAMLLoader:
        loader = self.loader_class(rf)
        loader.store = self.store
        return loader
