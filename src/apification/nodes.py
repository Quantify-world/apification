class ApiNodeMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ApiNodeMetaclass, cls).__new__(cls, name, parents, dct)
        for attr_name in dir(ret):
            node = getattr(ret, attr_name)
            if issubclass(node, ApiNode):
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
