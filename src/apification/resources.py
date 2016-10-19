from apification.actions import Action


class ResourceMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(ResourceMetaclass, cls).__new__(cls, name, parents, dct)
        for attrib in dir(ret):
            if not (attrib.startswith('__') or attrib.endswith('__')) and \
                    Action in getattr(getattr(ret, attrib, object), '__bases__',[]):
                setattr(getattr(ret, attrib), 'resource', ret)
        return ret

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
