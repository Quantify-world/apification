from itertools import chain, ifilter
from apification.utils.tpath.base import TPathError, TPathResolver


class ApiTreeTPathResolver(TPathResolver):
    def get_name(self, node):
        return node.name

    def get_root(self, node):
        return node.get_root_class()

    def iter_children(self, node):
        return node.iter_class_children()

    def get_child(self, node, name):
        try:
            return getattr(node, name)
        except AttributeError:
            raise TPathError()

    def get_parent(self, node):
        return node.parent_class




def parse_expression(expr, node):
    lexems = []
    for lex in lexems:
        lex.resolve()


def process_lexems(lexems, node):
    if not lexems:
        return node
    new_node = lexems[0].resolve()
    return process_lexems(lexems[1:], new_node)
    


