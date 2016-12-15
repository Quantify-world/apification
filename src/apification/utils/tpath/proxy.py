import itertools

from apification.utils.noninstantiable import Noninstantiable


class VirtualRoot(Noninstantiable):
    pass


class ProxyNode(Noninstantiable):
    def get_name(cls, node):
        raise NotImplementedError()

    def get_root(cls, node):
        raise NotImplementedError()

    def iter_children(cls, node):
        raise NotImplementedError()

    def get_child(cls, node, name):
        raise NotImplementedError()

    def get_parent(cls, node):
        raise NotImplementedError()

    def walk_subtree(cls, node):
        sub = [cls.walk_subtree(subnode) for subnode in cls.iter_children(node)]
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

    def iter_children(cls, node):
        if node is VirtualRoot:
            return iter([cls._get_implementation().get_root(node)])  # Lose noe FIXME!!!!!!
        else:
            return cls._get_implementation().iter_children(node)

    def get_child(cls, node, name):
        from apification.utils.tpath import TPathError
        if node is VirtualRoot:
            root = cls._get_implementation().get_root(node)
            root_name = cls._get_implementation().get_name()
    
            if root_name == name:
                return root
            else:
                raise TPathError()
        else:
            return cls._get_implementation().get_child(node, name)

    def get_parent(cls, node):
        if node is VirtualRoot:
            return None
        else:
            return cls._get_implementation().get_parent(node)
