#-*- coding: utf-8 -*-
from django.http import HttpResponseNotAllowed

from apification.serializers import Serializer


class ApiNodeMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        for node_name, node in ret.iter_children():
            node.parent_class = ret
            if not node.name:
                node.name = node_name.lower()
        ret.prepare_serializers()
        return ret

    @property
    def urls(cls):
        return cls.get_urls()
#  1. После создания класса ApiNode, но до инстанцирования его объектов мы должны знать где какой сериалайзер сидит.
#  2. Контекст, в котором работает сериалайзер нужно подсовывать в класс сериалайзера в момент его дефинишена.
#  3. Прошлый пункт можно исполнить, только есил делать это в метаклассе Node

class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
    _serializers_preparations = None
    parent_class = None  # in class will point to parent class, in instance will lazy-point to parent instance
    name = None

    def __init__(self, request, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = request
    
    @property
    def parent(self):
        if self.parent_class is None:
            return None
        if not hasattr(self, '_parent'):
            self._parent = self.parent_class(self.request, args=self.args, kwargs=self.kwargs)
        return self._parent

    @classmethod
    def prepare_serializers(cls):
        cls._serializers_preparations = []
        children_serializers_preparations = []
        for attr_name, node in cls.iter_children():
            children_serializers_preparations.extend(node._serializers_preparations)
        for attr_name, mapping in children_serializers_preparations:
            value = getattr(cls, attr_name, None)  # serializer or string
            if isinstance(value, type) and issubclass(value, Serializer):  # actual serializer - resolve finished
                value.node = cls  # set serializer context to it's container node
                for klass, name in mapping.iteritems():  # set real serializer to all requesting nodes
                    setattr(klass, name, value)
            else:  # string - need to look up in hierarchy
                if value is None:
                    entry = (attr_name, mapping)
                else:
                    mapping[cls] = attr_name
                    entry = (value, mapping)
                cls._serializers_preparations.append(entry)

    @classmethod
    def iter_children(cls):
        for attr_name in dir(cls):
            if (attr_name == 'parent_class'
                    or isinstance(getattr(type(cls), attr_name, None), property)):  # prevent accesing properties
                continue

            node = getattr(cls, attr_name)
            if (type(node) is cls.__metaclass__  # issubclass(node, ApiNode) # we can't reference ApiNode before class creation
                    and not attr_name.startswith('_')):
                yield attr_name, node


class ApiBranch(ApiNode):
    @classmethod
    def get_path(cls):
        raise NotImplementedError()

    @classmethod
    def entrypoint(cls, request, *args, **kwargs):
        # select proper action by http method
        for action_class in cls.iter_actions():
            if action_class.method == request.method:
                break
        else:
            raise HttpResponseNotAllowed()

        action = action_class(request, args=args, kwargs=kwargs)
        return action.run()

    @classmethod
    def iter_actions(cls):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if issubclass(attr, ApiLeaf):
                yield attr

    @classmethod
    def get_urls(cls):
        urls = []
        for node_name, node in cls.iter_children():
            urls.extend(node.urls)
        return urls

    @classmethod
    def construct_path(cls):
        path = ''
        if cls.parent_class:
            path += cls.parent_class.construct_path()
        path += cls.get_path()
        return path

    def get_object(self):
        raise NotImplementedError()

class ApiLeaf(ApiNode):
    pass

