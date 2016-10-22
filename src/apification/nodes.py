class ApiNodeMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        for attr_name in dir(ret):
            node = getattr(ret, attr_name)
            if (type(node) is cls and not attr_name.startswith('_') and
                    issubclass(node, ApiNode)):
                setattr(node, 'parent', ret)
        return ret

    @property
    def urls(cls):
        from apification.actions import Action

        urls = []
        for attr_name in dir(cls):
            node = getattr(cls, attr_name)
            if isinstance(node, Action):
                urls.extend(node.urls)
        return urls


class ApiNode(object):
    __metaclass__ = ApiNodeMetaclass
    parent = None

    def __init__(self, request, *args, **kwargs):
        for attrib_name in dir(self):
            attrib = getattr(self, attrib_name)
            if (not attrib_name.startswith('_') and
                    not attrib_name is 'parent' and # skip parent to prevent endless recursion
                    type(attrib) is ApiNodeMetaclass and issubclass(attrib, ApiNode)):
                instance = attrib(request, *args, **kwargs) # create child instance
                setattr(self, attrib_name, instance)        # attach child instance
                getattr(self, attrib_name).parent = self    # switch child's parent link from class to instance
