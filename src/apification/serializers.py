from apification.exceptions import ApiStructureError
from apification.utils import writeonce
from apification.utils.noninstantiable import NoninstantiableMeta
from apification import api_settings 

from apification.utils import tpath


@writeonce(name=None, parent_serializer=None)
class SerializierLinkMeta(NoninstantiableMeta):
    def __call__(cls, node_path, serializer_name, generation_method_name):
        cls.node_path = node_path
        cls.serializer_name = serializer_name
        cls.generation_method_name = generation_method_name
        return cls


class BaseSerializerLink(object):
    __metaclass__ = SerializierLinkMeta

    def retrieve_serializer(cls):
        try:
            node_class = tpath.parse(cls.parent_serializer.node_class, cls.node_path)
        except tpath.TPathError as e:
            raise ApiStructureError(u'Invalid path "%s": e' % (cls.node_path, e))  # TODO: more verbose message
        return getattr(node_class, cls.serializer_name)

    def instance_generator(cls, node):
        if not hasattr(node, cls.generation_method_name):
            raise ApiStructureError(u'Error resolving %s: %s generation_method_name not found in %s' % (
                cls, cls.generation_method_name, node))
        return getattr(node, cls.generation_method_name)()

    def from_serializer(cls):
        raise NotImplementedError()


class Single(BaseSerializerLink):
    def from_serializer(cls, node):
        return cls.retrieve_serializer().from_object(cls.instance_generator(node).next())


class List(BaseSerializerLink):
    def from_serializer(cls, node):
        return [cls.retrieve_serializer().from_object(i) for i in cls.instance_generator(node)]


class Dict(BaseSerializerLink):
    def from_serializer(cls, node):
        return dict((k, cls.retrieve_serializer().from_object(i)) for k, i in cls.instance_generator(node))


@writeonce(node_class=None)
class SerializerMeta(NoninstantiableMeta):
    def __new__(cls, name, parents, dct):
        ret = super(SerializerMeta, cls).__new__(cls, name, parents, dct)

        for attr_name, link in ret._iter_links():
            link.parent_serializer = ret
            link.name = attr_name.lower()

        return ret

    def _iter_links(cls):
        for attr_name in dir(cls):
            if (attr_name.startswith('_') or hasattr(cls, attr_name)):
                continue

            link = getattr(cls, attr_name)
            if (isinstance(link, SerializierLinkMeta)):
                yield attr_name, link


class Serializer(object):
    __metaclass__ = SerializerMeta

    @classmethod
    def get_backend_registry(cls):
        return getattr(cls, 'backends', api_settings.SERIALIZER_BACKENDS)

    @classmethod
    def from_object(cls, node):
        assert type(node) is cls.node_class  # inheritance match is not accepted here
        registry = cls.get_backend_registry()
        data = registry.run(instance=node.instance)
        for name, link in cls._iter_links():
            data[name] = link.from_serializer(node)
        return data
