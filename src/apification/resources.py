from apification.actions import Action


class ResourceMetaclass(type):
    def __new__(cls, *args, **kwargs):
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, (Action, Resource)):
                attr.resource = cls
        return int.__new__(cls, *args, **kwargs)

    @property
    def urls(cls):
        urls = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Action):
                urls.append(attr.get_url_entry())
        return urls


class Resource(object):
    __metaclass__ = ResourceMetaclass


class DjangoResource(Resource):
    pass
