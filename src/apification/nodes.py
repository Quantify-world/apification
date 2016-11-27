#-*- coding: utf-8 -*-
from django.http import HttpResponseNotAllowed, HttpRequest, HttpResponse

from apification.serializers import NodeSerializer
from apification.exceptions import ApiStructureError, NodeParamError
from apification.params import RequestParam
from apification.utils import writeonce


class SerializerBail(list):
    def __init__(self, node_class):
        super(SerializerBail, self).__init__()
        self.node_class = node_class
        node_class._serializers_preparations = self

    def init_action(self):
        self.add(attr_name=self.node_class.serializer, mapping={self.node_class: 'serializer'})

    def iter_sb_children(self):
        for attr_name, subnode_class in self.node_class.iter_children():
            for attr_name, mapping in subnode_class._serializers_preparations or ():
                yield (attr_name, mapping)

    def add(self, attr_name, mapping):
        self.append((attr_name, mapping))

    def resolve(self, serializer, mapping):
        serializer.node_class = self.node_class  # set serializer context to it's container node
        for klass, name in mapping.iteritems():  # set real serializer to all requesting nodes
            setattr(klass, name, serializer)


class ApiNodeMetaclass(type):
    parent_class = writeonce(None, writeonce_msg=u'Duplicate in API tree: %(instance)s already has parent %(old_value)s though %(value)s can not be set as new parent')
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        # Initializing internal class attributes
        ret._serializers_preparations = None

        for node_name, node_class in ret.iter_children():
            node_class.parent_class = ret
            if not node_class.name:
                node_class.name = node_name.lower()
        ret.prepare_serializers()
        return ret

    @property
    def urls(cls):
        cls.get_root_class()  # check for loops
        return cls.get_urls()
    
    def __str__(cls):
        if not hasattr(cls, '_strval'):
            s = cls.__name__
            node = cls
            i = 0
            N = 10
            while node.parent_class is not None and i < N:
                s = node.parent_class.__name__+'.'+s
                node = node.parent_class
                i += 1
            if i == N:
                s = ' ...%s' % s
            else:
                s = '.%s' % s
        
            cls._strval = '%s%s' % (node.__module__, s)
        return cls._strval

class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
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
        sb = SerializerBail(cls)
        for attr_name, mapping in sb.iter_sb_children():
            value = getattr(cls, attr_name, None)  # current class attribute name fetched from children
            if isinstance(value, type) and issubclass(value, NodeSerializer):  # actual serializer - resolve finished
                sb.resolve(value, mapping)
            elif isinstance(value, basestring):  # string - need to look up in hierarchy
                mapping[cls] = attr_name
                sb.add(value, mapping)
            elif value is None:  # skip next level up
                sb.add(attr_name, mapping)
            else:  # not suitable type
                raise ApiStructureError("Serializer for %s must be NodeSerializer subclass or string, not %s" % (cls, type(value)))

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

    @classmethod
    def get_root_class(cls):
        seen = set()
        node_class = cls
        while node_class.parent_class is not None:
            if node_class in seen:
                raise ApiStructureError(u"API tree is not actually tree: loop found at %s" % node_class)
            seen.add(node_class)
            node_class = node_class.parent_class
        return node_class

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
