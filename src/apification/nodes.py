#-*- coding: utf-8 -*-
from django.http import HttpResponseNotAllowed, HttpRequest, HttpResponse

from apification.serializers import Serializer
from apification.exceptions import ApiStructureError, NodeParamError
from apification.params import RequestParam


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


class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass

    _serializers_preparations = None
    parent_class = None
    name = None

    def __init__(self, param_values):
        for param_name, param_class in self.get_params().iteritems():
            value = param_values.get(param_name)
            param_class.is_valid(self, value)
        self.param_values = param_values

    @classmethod
    def get_name(cls):
        return cls.name or cls.__name__.lower()  # for root node

    @classmethod
    def construct_path(cls):
        raise NotImplementedError()

    @property
    def parent(self):
        if self.parent_class is None:
            return None
        if not hasattr(self, '_parent'):
            self._parent = self.parent_class(self.param_values)
        return self._parent

    @classmethod
    def get_params(cls):
        if not hasattr(cls, '_params'):
            cls._params = {}
            if cls.parent_class is not None:
                cls._params.update(cls.parent_class.get_params())
            cls._params.update(cls.get_local_params())
        return cls._params

    @classmethod
    def get_local_params(cls):
        return {'request': RequestParam}

    @classmethod
    def prepare_serializers(cls):
        cls._serializers_preparations = []
        children_serializers_preparations = []
        for attr_name, node in cls.iter_children():
            children_serializers_preparations.extend(node._serializers_preparations)
        for attr_name, mapping in children_serializers_preparations:
            value = getattr(cls, attr_name, None)  # serializer or string
            if isinstance(value, type) and issubclass(value, Serializer):  # actual serializer - resolve finished
                value.node_class = cls  # set serializer context to it's container node
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
            if (attr_name == 'parent_class' or attr_name.startswith('_')):
                continue

            node = getattr(cls, attr_name)
            if (type(node) is cls.__metaclass__):  # issubclass(node, ApiNode) # we can't reference ApiNode before class creation):
                yield attr_name, node

    def iter_ascedants(self, include_self=False):
        if include_self:
            yield self
        node = self
        while node.parent is not None:
            node = node.parent
            yield node

    def serialize(self, obj, serializer_name='default_serializer'):
        serializer_class = getattr(self, serializer_name)
        return serializer_class.from_object(obj, node=self)

    @classmethod
    def render(cls, data):
        from apification.renderers import JSONRenderer
        data = JSONRenderer().render(data)
        return HttpResponse(data)


class ApiBranch(ApiNode):
    @classmethod
    def get_path(cls):
        return cls.get_name() + '/'

    @classmethod
    def entrypoint(cls, request, *args, **kwargs):
        # select proper action by http method
        for action_class in cls.iter_actions():
            if action_class.method == request.method:
                break
        else:
            raise HttpResponseNotAllowed()

        param_values = {}
        for param_name, param_class in action_class.get_params().iteritems():
            param_values[param_name] = param_class.construct(cls, request, args, kwargs)
        try:
            action = action_class(param_values)
            return action.run()
        except NodeParamError:
            return HttpRequest(status=500)  # TODO: report, logging etc

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


class ApiLeaf(ApiNode):
    pass
