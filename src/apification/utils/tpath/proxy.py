import itertools

from apification.utils.noninstantiable import NoninstantiableMeta, Noninstantiable


class VirtualRoot(object):
    class __metaclass__(NoninstantiableMeta):
        def __str__(cls):
            return u'#document'


class ProxyNode(Noninstantiable):
    def get_name(cls, node):
        raise NotImplementedError()

    def get_root(cls, context_node, node):
        raise NotImplementedError()

    def iter_children(cls, context_node, node):
        raise NotImplementedError()

    def get_child(cls, context_node, node, name):
        raise NotImplementedError()

    def get_parent(cls, context_node, node):
        raise NotImplementedError()

    def walk_subtree(cls, context_node, node):
        sub = [cls.walk_subtree(context_node, subnode) for subnode in cls.iter_children(context_node, node)]
        return itertools.chain([node], *sub)


class RootableProxyMixin(ProxyNode):
    """
    Intended to be used as parent class in dynamic inheritance for virtual root class.
    """

    def _get_implementation(cls):
        mro = cls.mro()
        try:
            i = mro.index(RootableProxyMixin)
        except ValueError:
            raise RuntimeError(u'Unable to find VirtualRootMixin in %s ancestor classes' % cls)
        assert mro[i+1] is not ProxyNode, u'Invalid inheritance order'
        return mro[i+1]

    def make_rootable(cls, klass):
        assert not issubclass(klass, RootableProxyMixin)
        return type('Proxy', (cls, klass), {})

    def get_name(cls, node):
        if node is VirtualRoot:
            return '#document'
        else:
            return cls._get_implementation().get_name(node)

    def iter_children(cls, context_node, node):
        if node is VirtualRoot:
            return iter([cls._get_implementation().get_root(context_node, context_node)])
        else:
            return cls._get_implementation().iter_children(context_node, node)

    def get_child(cls, context_node, node, name):
        from apification.utils.tpath import TPathError
        if node is VirtualRoot:
            root = cls._get_implementation().get_root(context_node, context_node)
            root_name = cls._get_implementation().get_name()
    
            if root_name == name:
                return root
            else:
                raise TPathError()
        else:
            return cls._get_implementation().get_child(context_node, node, name)

    def get_parent(cls, context_node, node):
        if node is VirtualRoot:
            return None
        else:
            return cls._get_implementation().get_parent(context_node, node)
