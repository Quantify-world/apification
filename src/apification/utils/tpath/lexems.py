from itertools import chain

from apification.utils.tpath.base import TPathParser, BaseLexem


@TPathParser.separator
class SlashSeparator(BaseLexem):
    pattern = r'/'

    def resolve(self, iterator=None):
        from apification.utils.tpath.proxy import VirtualRoot

        if iterator is None:
            yield VirtualRoot
            return
        for i in iterator:
            yield i


@TPathParser.separator
class DoubleSlashSeparator(BaseLexem):
    pattern = r'//'
    priority = 200  # before Slash
    
    def resolve(self, iterator):
        from apification.utils.tpath.proxy import VirtualRoot
        if iterator is None:
            iterator = iter([VirtualRoot])
        return chain(*[self.proxy.walk_subtree(self.node, i) for i in iterator])


@TPathParser.lexem
class Dot(BaseLexem):
    pattern = r'\.'

    def resolve(self, iterator):
        if iterator is None:
            return iter([self.node])
        return iterator


@TPathParser.lexem
class DoubleDot(BaseLexem):
    pattern = r'\.\.'
    priority = 200

    def resolve(self, iterator):
        if iterator is None:
            iterator = iter([self.node])
        for node in iterator:
            parent = self.proxy.get_parent(self.node, node)
            if parent is not None:
                yield parent


@TPathParser.lexem
class NodeName(BaseLexem):
    pattern = r'[a-zA-Z_][a-zA-Z_0-9]*'
    priority = 10

    def __repr__(self):
        return u'<node name(%s)>' % self.token

    def resolve(self, iterator):
        if iterator is None:
            iterator = iter([self.node])

        for node in iterator:
            for subnode in self.proxy.iter_children(self.node, node):
                if self.token == self.proxy.get_name(subnode):
                    yield subnode


@TPathParser.lexem
class Asterisk(BaseLexem):
    pattern = r'\*'
    priority = 10

    def resolve(self, iterator):
        if iterator is None:
            iterator = iter([self.node])

        for node in iterator:
            for subnode in self.proxy.iter_children(self.node, node):
                yield subnode
