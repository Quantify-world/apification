class SkipBackend(Exception):
    pass


class BackendRegistry(list):
    def __init__(self, registry_name, iterable):
        super(BackendRegistry, self).__init__(iterable)
        self.registry_name = registry_name

    def __add__(self, value):
        if value.registry_name != self.registry_name:
            raise TypeError(u'Unable to create registry with backends with different registry names')
        if isinstance(value, BackendRegistry):
            self.extend(value)
        else:
            self.append(value)
        return self

    def run(self, *args, **kwargs):
        for backend in self:
            try:
                return backend.run(*args, **kwargs)
            except SkipBackend:
                continue
        raise RuntimeError(u'No one from the following backends matches: %s' % ', '.join(map(str, self)))


class BackendMetaclass(type):
    def __add__(cls, value):
        if cls.registry_name != value.registry_name:
            raise TypeError(u'Unable to create registry with backends with different registry names')
        if isinstance(value, BackendRegistry):
            return BackendRegistry(cls.registry_name, [cls]) + value
        else:
            return BackendRegistry(cls.registry_name, (cls, value))


class BaseBackend(object):
    __metaclass__ = BackendMetaclass
    registry_name = None
    
    @classmethod
    def run(cls, *args, **kwargs):
        raise NotImplementedError()
