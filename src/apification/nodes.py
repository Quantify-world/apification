from django.conf.urls import url
from django.http import HttpResponseNotAllowed


class ApiNodeMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        for attr_name in dir(ret):
            if isinstance(getattr(cls, attr_name), property):
                # prevent accesing properties
                continue
            node = getattr(ret, attr_name)
            if (type(node) is cls  # issubclass(node, ApiNode) # we can't reference ApiNode before class creation
                    and not attr_name.startswith('_')):
                setattr(node, 'parent', ret)
        return ret

    @property
    def urls(cls):
        urls = []
        for attr_name in dir(cls):
            node = getattr(cls, attr_name)
            if isinstance(node, ApiNode):
                urls.extend(node.urls)
        return urls


class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
    parent = None  # in class will point to parent class, in instance will lazy-point to parent instance

    def __init__(self, request, args, kwargs):
        # lazy instantiating of parent
        def fget_parent(self):
            if not hasattr(self, '_parent_instance'):
                self._parent_instance = self.__class__.parent(request, args=args, kwargs=kwargs)
            return self._parent_instance

        self.parent = property(fget_parent)


class ApiBranch(ApiNode):
    @classmethod
    def get_path(cls):
        raise NotImplementedError()

    @classmethod
    def view(cls, request, *args, **kwargs):
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


class ApiLeaf(ApiNode):
    pass

