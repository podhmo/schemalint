from yaml.error import Mark
from schemalint.errors import LintError
from schemalint.entity import Lookup


# TODO: move


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

        start_mark = copy.deepcopy(mark)
        start_mark.column = 0
        end_mark = copy.deepcopy(mark)
        end_mark.column = -1
        return (start_mark, end_mark)

    def lookup_kvpair(self, node, k):  # todo: rename
        for knode, vnode in node.value:
            if knode.value == k:
                return knode, vnode
