from apification.utils.tpath.base import TPathError, TPathParser, BaseLexem
from apification.utils.tpath.proxy import ProxyNode, VirtualRoot


class ApiTreeProxy(ProxyNode):
    def get_name(cls, node):
        return node.name

    def get_root(cls, context_node, node):
        return node.get_root_class()

    def iter_children(cls, context_node, node):
        return node.children.itervalues()

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


@TPathApiTreeParser.lexem
class SerializerName(BaseLexem):
    pattern = r'@[a-zA-Z_][a-zA-Z_0-9.]*'

    def __repr__(self):
        return u'<serializer name(%s)>' % self.token[1:]

    def resolve(self, iterator):
        if iterator is None:
            iterator = iter([self.node])

        serializer_name = self.token[1:]
        for node in iterator:
            for name, attr_name in TODO.serializers:
                if name == serializer_name:
                    yield TODO.get(node, name)  # TODO is future registry of serializers
