from itertools import chain, ifilter

from apification.utils.tpath.base import TPathResolver, BaseLexem


@TPathResolver.lexem
class Slash(BaseLexem):
    pattern = r'/'

    def resolve(self, iterator):
        if iterator is None:
            yield self.parser.get_root(self.node)
            return

        for node in iterator:
            for subnode in self.parser.iter_children(node):
                yield subnode


@TPathResolver.lexem
class DoubleSlash(BaseLexem):
    pattern = r'//'
    priority = 200  # before Slash
    
    def resolve(self, iterator):
        if iterator is None:
            root = self.parser.get_root(self.node)
            return self.resolve(iter([root]))
        return chain(*[ifilter(lambda x: x!=i, self.parser.walk_subtree(i)) for i in iterator])


@TPathResolver.lexem
class Dot(BaseLexem):
    pattern = r'\.'

    def resolve(self, iterator):
        if iterator is None:
            return iter([self.node])
        return iterator


@TPathResolver.lexem
class DoubleDot(BaseLexem):
    pattern = r'\.\.'

    def resolve(self, iterator):
        for node in iterator:
            parent = self.parser.get_parent(node)
            if parent is not None:
                yield parent


@TPathResolver.lexem
class NodeName(BaseLexem):
    pattern = r'[a-zA-Z_][a-zA-Z_0-9]*'
    priority = 10

    def __repr__(self):
        return u'<node name(%s)>' % self.token

    def resolve(self, iterator):
        def f(node):
            return self.parser.get_name(node) == self.token
        return ifilter(f, iterator)
