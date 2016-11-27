from itertools import chain

class writeonce(object):
    def __init__(self, *args, **kwargs):
        self.name = None
        self.__doc__ = kwargs.pop('doc', None)
        self.args = args  # for klass decorator case
        self.kwargs = kwargs
        if args:  # for property case
            self.default = args[0]

    def __call__(self, klass):
        for attr_name in chain(self.args, self.kwargs.iterkeys()):
            if hasattr(klass, attr_name):
                raise TypeError(u'%s already has "%s" attribute: unable to add writeonce property' % (klass, attr_name))
            default_args = []
            if attr_name in self.kwargs:
                default_args.append(self.kwargs[attr_name])
            setattr(klass, attr_name, type(self)(*default_args))
        return klass

    @staticmethod
    def iter_bases_attrs(klass):
        iterables = []
        for base in reversed(type.mro(klass)):
            iterables.append(base.__dict__.iteritems())
        return chain(*iterables)

    def get_name(self, obj):
        if not self.name:
            for attr_name, attr_value in self.iter_bases_attrs(obj.__class__):
                if attr_value is self:
                    self.name = attr_name
        return self.name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        key = '__writeonce_value_%s' % self.get_name(instance)
        if hasattr(instance, key):
            return getattr(instance, key)
        elif hasattr(self, 'default'):
            return self.default
        else:
            raise AttributeError(u"%s has no attribute '%s'" % (instance, self.get_name(instance)))

    def __set__(self, instance, value):
        key = '__writeonce_value_%s' % self.get_name(instance)
        if not hasattr(instance, key):
            setattr(instance, key, value)
        elif getattr(instance, key) is value:
            pass # warn
        else:
            raise TypeError(u"immutable property %s of %s can't be modifyed" % (self.get_name(instance), instance))
        
    def __delete__(self, instance):
        raise TypeError(u"immutable property %s of %s can't be deleted" % (self.get_name(instance), instance))
