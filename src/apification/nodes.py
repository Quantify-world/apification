#-*- coding: utf-8 -*-
from django.http import HttpResponseNotAllowed

from apification.serializers import Serializer
from apification.exceptions import ApiStructureError


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
        for param_name, param_class in self.params.iteritems():
            value = param_values.get(param_name)
            param_class.is_valid(self, value)
        self.param_values = param_values
    
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
            cls.params.update(cls.params)
        return cls._params

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
            if (attr_name == 'parent_class'
                    or isinstance(getattr(type(cls), attr_name, None), property)):  # prevent accesing properties
                continue

            node = getattr(cls, attr_name)
            if (type(node) is cls.__metaclass__  # issubclass(node, ApiNode) # we can't reference ApiNode before class creation
                    and not attr_name.startswith('_')):
                yield attr_name, node

    def iter_ascedants(self, include_self=False):
        if include_self:
            yield self
        node = self
        while node.parent is not None:
            node = node.parent
            yield node

    def get_serializer(self, serializer_name='serializer'):
        serializer_class = getattr(self, serializer_name)
        for node in self.iter_ascedants(include_self=True):
            if isinstance(node, serializer_class.node_class):
                break
        else:
            raise ApiStructureError(u'Serializer %s not found in asdendants for %s' % (serializer_class, self))
        return serializer_class(node=node)


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

        param_values = {}
        for param_name, param_class in action_class.params.iteritems():
            param_values[param_name] = param_class.contruct(cls, request, args, kwargs)
        try:
            action = action_class(param_values)
            return action.run()
        except NodeParamError as e:
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

    def get_object(self):
        raise NotImplementedError()


class ApiLeaf(ApiNode):
    pass
