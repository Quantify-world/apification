from apification.exceptions import ApiStructureError
from apification.utils import writeonce
from apification.utils.noninstantiable import NoninstantiableMeta
from apification import api_settings 

from apification.utils import tpath


class SerializierLinkMeta(NoninstantiableMeta):
    def __call__(cls, node_path, serializer_name, generation_method):
        cls.node_path = node_path
        cls.serializer_name = serializer_name
        cls.generation_method = generation_method
        return cls


class BaseSerializerLink(object):
    __metaclass__ = SerializierLinkMeta

    parent_serializer = None  # TODO: fill in Serializer__init__

    def retrieve_serializer(cls):
        try:
            node = tpath.parse(cls.parent_serializer.node, cls.node_path)
        except tpath.TPathError as e:
            raise ApiStructureError(u'Invalid path "%s": e' % (cls.node_path, e))  # TODO: more verbose message
        return getattr(node, cls.serializer_name)

    def make_node_instance(cls):  # naming node iter?
        return cls.generation_method()  # TODO: args?

    def from_serializer(cls):
        raise NotImplementedError()


class SingleSerializerLink(BaseSerializerLink):
    def from_serializer(cls):
        return cls.retrieve_serializer().from_object(cls.make_node_instance())

class ListSerializerLink(BaseSerializerLink):
    def from_serializer(cls):
        return [cls.retrieve_serializer().from_object(i) for i in cls.make_node_instance()]

class DictSerializerLink(BaseSerializerLink):
    def from_serializer(cls):
        return dict((k, cls.retrieve_serializer().from_object(i)) for k, i in cls.make_node_instance())


@writeonce(parent_serializer=None, name=None, node_class=None)
class SerializerMeta(NoninstantiableMeta):
    def __new__(cls, name, parents, dct):
        ret = super(SerializerMeta, cls).__new__(cls, name, parents, dct)

        for attr_name, sub_serializer in cls._iter_with_name():
            sub_serializer.parent_serializer = ret
            assert sub_serializer.name is None
            sub_serializer.name = attr_name.lower()

        return ret

    def __iter__(cls):
        for attr_name, sub_serializer in cls._iter_with_name():
            yield sub_serializer

    def _iter_with_name(cls):
        for attr_name in dir(cls):
            if (attr_name.startswith('_') or attr_name == 'node_class'):
                continue

            sub_serializer = getattr(cls, attr_name)
            if (type(sub_serializer) is cls.__metaclass__):
                yield attr_name, sub_serializer


class Serializer(object):
    __metaclass__ = SerializerMeta

    @classmethod
    def get_backend_registry(cls):
        return getattr(cls, 'backends', api_settings.SERIALIZER_BACKENDS)

    @classmethod
    def from_children(cls, obj, node):
        ret = {}
        for sub_serializer in cls:
            ret[sub_serializer.name] = sub_serializer.from_object(obj, node)
        return ret

    @classmethod
    def from_object(cls, obj, node):  # TODO: rework
        node = cls.resolve_node(node)
        ret = cls.from_children(obj, node)
        registry = cls.get_backend_registry()
        ret.update(registry.run(instance=obj))
        return ret

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


class ListSerializer(Serializer):
    serializer_name = 'default_serializer'  # internal serializer name

    @classmethod
    def from_object(cls, obj, node):
        node = cls.resolve_node(node)
        ret = []
        for subnode in cls.iter_nodes(node):
            data = subnode.serialize(subnode.get_object(), serializer_name=cls.serializer_name)
            ret.append(data)
        return ret

    @classmethod
    def iter_nodes(cls, node):
        return iter(node)
