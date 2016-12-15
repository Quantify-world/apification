#-*- coding: utf-8 -*-
from django.http import HttpResponseNotAllowed, HttpResponse

from apification.serializers import Serializer
from apification.exceptions import ApiStructureError
from apification.utils import writeonce, instancevisible


class SerializerBail(list):
    def __init__(self, node_class):
        super(SerializerBail, self).__init__()
        self.node_class = node_class
        node_class._serializers_preparations = self

    def init_action(self):
        self.add(attr_name=self.node_class.serializer, mapping={self.node_class: 'serializer'})

    def iter_sb_children(self):
        for subnode_class in self.node_class.iter_class_children():
            for attr_name, mapping in subnode_class._serializers_preparations or ():
                yield (attr_name, mapping)

    def add(self, attr_name, mapping):
        self.append((attr_name, mapping))

    def resolve(self, serializer, mapping):
        serializer.node_class = self.node_class  # set serializer context to it's container node
        for klass, name in mapping.iteritems():  # set real serializer to all requesting nodes
            setattr(klass, name, serializer)


class ApiNodeMetaclass(instancevisible.Meta):
    parent_class = writeonce(None, writeonce_msg=u'Duplicate in API tree: %(instance)s already has parent %(old_value)s though %(value)s can not be set as new parent')

    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        ret._children = []  # not in __init__ because will be used here

        for asc in ret.mro():
            for attr_name, node_class in asc.__dict__.iteritems():
                if (attr_name == 'parent_class' or attr_name.startswith('_')):
                    continue
    
                if (type(node_class) is ret.__metaclass__):  # issubclass(node, ApiNode) # we can't reference ApiNode before class creation):
                    if asc is ret:  # current class
                        ret.add_child_class(attr_name, node_class)
                    else:
                        raise ApiStructureError(u'Class %s has parent class %s with defined child node %s.' % (ret, asc, node_class))
        return ret

    def __init__(cls, name, parents, dct):
        cls._serializers_preparations = None
        cls.prepare_serializers()

    def add_child_class(cls, name, node_class):
        node_class.name = name
        node_class.parent_class = cls
        cls._children.append(node_class)

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
                s = node.parent_class.__name__ + '.' + s
                node = node.parent_class
                i += 1
            if i == N:
                s = '...%s' % s
            else:
                s = '%s' % s
        
            cls._strval = s
        return cls._strval

    @instancevisible
    @property
    def parent(self):
        if self.__class__.parent_class is None:
            return None
        if not hasattr(self, '_parent'):
            self._parent = self.__class__.parent_class(self.request, self.args, self.kwargs)
        return self._parent

    @instancevisible
    def prepare_serializers(cls):
        sb = SerializerBail(cls)
        for attr_name, mapping in sb.iter_sb_children():
            value = getattr(cls, attr_name, None)  # current class attribute name fetched from children
            if isinstance(value, type) and issubclass(value, Serializer):  # actual serializer - resolve finished
                sb.resolve(value, mapping)
            elif isinstance(value, basestring):  # string - need to look up in hierarchy
                mapping[cls] = attr_name
                sb.add(value, mapping)
            elif value is None:  # skip next level up
                sb.add(attr_name, mapping)
            else:  # not suitable type
                raise ApiStructureError("Serializer for %s must be Serializer subclass or string, not %s" % (cls, type(value)))

    @instancevisible
    def iter_class_children(cls):
        return iter(cls._children)

    @instancevisible
    def get_root_class(cls):
        seen = set()
        node_class = cls
        while node_class.parent_class is not None:
            if node_class in seen:
                raise ApiStructureError(u"API tree is not actually tree: loop found at %s" % node_class)
            seen.add(node_class)
            node_class = node_class.parent_class
        node_class.name = node_class.__name__  # root element has no parent, so set name here
        return node_class

    def render(self, data):
        from apification.renderers import JSONRenderer
        data = JSONRenderer().render(data)
        return HttpResponse(data)


class NoInstance(object):
    class __metaclass__(type):
        @instancevisible
        def __nonzero__(self):
            return False


class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
    name = None

    def __init__(self, request, args, kwargs, instance=NoInstance):
        self.request = request
        self.args = args
        self.kwargs = kwargs
        if instance is NoInstance:
            self.instance = self.make_instance()
            self.instance_from_request = True
        else:
            self.instance = instance
            self.instance_from_request = False

    def make_instance(self):
        raise NotImplementedError()

    @classmethod
    def construct_path(cls):
        raise NotImplementedError()

    def iter_ascedants(self, include_self=False):
        if include_self:
            yield self
        node = self
        while node.parent is not None:
            node = node.parent
            yield node

    def serialize(self, serializer_name='default_serializer'):
        serializer_class = getattr(self, serializer_name)
        return serializer_class.from_object(node=self)


class ApiBranch(ApiNode):
    @classmethod
    def construct_path(cls):
        path = ''
        if cls.parent_class:
            path += cls.parent_class.construct_path()
        path += cls.get_path()
        return path

    @classmethod
    def get_path(cls):
        return cls.name.lower() + '/'

    @classmethod
    def entrypoint(cls, request, *args, **kwargs):
        # select proper action by http method
        for action_class in cls.iter_actions():
            if action_class.method == request.method:
                break
        else:
            raise HttpResponseNotAllowed()

        action = action_class(request, args, kwargs)
        return action.run()

    @classmethod
    def iter_actions(cls):
        for child in cls.iter_class_children():
            if issubclass(child, ApiLeaf):
                yield child

    @classmethod
    def get_urls(cls):
        urls = []
        for node in cls.iter_class_children():
            urls.extend(node.urls)
        return urls


class ApiLeaf(ApiNode):
    def make_instance(self):
        return None  # actions do not require any particular instances
