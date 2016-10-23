from django.http import HttpResponseNotAllowed


class ApiNodeMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        for node_name, node in ret.iter_children():
            node.parent = ret
            if not node.name:
                node.name = node_name.lower()
        return ret

    @property
    def urls(cls):
        return cls.get_urls()


class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
    parent = None  # in class will point to parent class, in instance will lazy-point to parent instance
    name = None

    def __init__(self, request, args, kwargs):
        self.args = args
        self.kwargs = kwargs
        self.request = request
        # lazy instantiating of parent
        def fget_parent(self):
            if not hasattr(self, '_parent_instance'):
                self._parent_instance = self.__class__.parent(request, args=args, kwargs=kwargs)
            return self._parent_instance

        self.parent = property(fget_parent)

    @classmethod
    def iter_children(cls, filter_class=None):
        if filter_class is None:
            filter_class = cls
        for attr_name in dir(cls):
            if (attr_name == 'parent'
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

    @classmethod
    def get_urls(cls):
        urls = []
        for node_name, node in cls.iter_children():
            urls.extend(node.urls)
        return urls

    @classmethod
    def construct_path(cls):
        path = ''
        if cls.parent:
            path += cls.parent.construct_path()
        path += cls.get_path()
        return path


class ApiLeaf(ApiNode):
    pass

