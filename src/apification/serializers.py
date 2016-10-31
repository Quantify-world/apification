from django.http import HttpResponse


class SerializerMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(SerializerMetaclass, cls).__new__(cls, name, parents, dct)
        return ret

    def __call__(cls, node, obj):
        cls.run(node, obj)


class Serializer(object):
    node_class = None

    def __init__(self):
        raise TypeError(u'%s is not instantiatiable entity' % self.__class__)

    @classmethod
    def from_object(cls, node, obj):
        assert isinstance(node, cls.node_class)
        raise NotImplementedError()


class ListSerializer(Serializer):
    serializer_name = 'default_serializer'  # internal serializer name

    @classmethod
    def from_object(cls, node, obj):
        ret = []
        for node in cls.iter_nodes(node):
            data = node.serialize(node.get_object(), serializer_name=cls.serializer_name)
            ret.append(data)
        return ret

    @classmethod
    def iter_nodes(cls, node):
        return iter(node)
