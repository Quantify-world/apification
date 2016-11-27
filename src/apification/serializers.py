from apification.exceptions import ApiStructureError
from apification.utils import writeonce
from apification.utils.noninstantiable import NoninstantiableMeta

class SerializerMetaclass(NoninstantiableMeta):
    def __new__(cls, name, parents, dct):
        ret = super(SerializerMetaclass, cls).__new__(cls, name, parents, dct)
        for name, sub_serializer in ret:
            sub_serializer.parent_serializer = ret
            if sub_serializer.name is None:
                sub_serializer.name = name.lower()
        return ret

    def __iter__(cls):
        for attr_name in dir(cls):
            if (attr_name.startswith('_') or attr_name == 'node_class'):
                continue
        
            sub_serializer = getattr(cls, attr_name)
            if (type(sub_serializer) is cls.__metaclass__):
                yield attr_name, sub_serializer

@writeonce(parent_serializer=None, name=None)
class Serializer(object):
    __metaclass__ = SerializerMetaclass

    def __init__(self):
        raise TypeError(u'%s is not instantiatiable entity' % self.__class__)

    @classmethod
    def from_object(cls, obj, **kwargs):
        ret = {}
        for name, sub_serializer in cls:
            ret[sub_serializer.name or name.lower()] = sub_serializer.from_object(obj, **kwargs)
        return ret


class NodeSerializer(Serializer):
    node_class = writeonce(None)

    @classmethod
    def get_node_class(cls):
        ser = cls
        while ser.parent_serializer:
            if ser.node_class is not None:
                return ser.node_class
            ser = ser.parent_serializer
        if ser.node_class is not None:
            return ser.node_class
        raise ApiStructureError(u'NodeSerializer %s has no parent context (node_class attribute)' % cls)

    @classmethod
    def resolve_node(cls, node):
        node_class = cls.get_node_class()
        for upnode in node.iter_ascedants(include_self=True):
            if isinstance(upnode, node_class):
                break
        else:
            raise ApiStructureError(u'Serializer %s not found in asdendants for %s' % (cls, node))
        return upnode

    @classmethod
    def from_object(cls, obj, node):  # TODO: refactor from_object to be more extensible
        node = cls.resolve_node(node)
        return super(NodeSerializer, cls).from_object(obj, node=node)


class ListSerializer(NodeSerializer):
    serializer_name = 'default_serializer'  # internal serializer name

    @classmethod
    def from_object(cls, obj, node):
        node = cls.resolve_node(node)
        ret = []
        for node in cls.iter_nodes(node):
            data = node.serialize(node.get_object(), serializer_name=cls.serializer_name)
            ret.append(data)
        return ret

    @classmethod
    def iter_nodes(cls, node):
        return iter(node)
