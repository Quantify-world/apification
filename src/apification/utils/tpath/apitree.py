from apification.utils.tpath.base import TPathError, TPathParser
from apification.utils.tpath.proxy import ProxyNode, VirtualRoot


class ApiTreeProxy(ProxyNode):
    def get_name(cls, node):
        return node.name

    def get_root(cls, context_node, node):
        return node.get_root_class()

    def iter_children(cls, context_node, node):
        return node.iter_class_children()

    def get_child(cls, context_node, node, name):
        try:
            return getattr(node, name)
        except AttributeError:
            raise TPathError()

    def get_parent(cls, context_node, node):
        if node.parent_class is None:
            return VirtualRoot
        return node.parent_class


class TPathApiTreeParser(TPathParser):
    proxy = ApiTreeProxy
