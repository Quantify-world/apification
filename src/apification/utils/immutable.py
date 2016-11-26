class immutable(object):
    """Property-like decorator for creating immutable attributes.
    These attributes can be set only once and can't be modified or deleted afterwards.
    
    Decorator-method for giving property a setter is called 'init' instead of
    traditional for common properties name 'setter.
    
    Usage:
    
        class A(object):
            @immutable
            def x(self):
                return self._x
            
            @x.init
            def x(self, value):
                self._x = value
    
    Alternative usage:

        class A(object):
            def x(self):
                return self._x
                
            def initx(self, value):
                self._x = value
            x = immutable(x, initx)
    ...
        a = A()
        a.x = 5 # ok
        a.x = 6 # TypeError: immutable property x of <__main__.A object> can't be modifyed
        del a.x # TypeError: immutable property x of <__main__.A object> can't be deleted
    """
    
    def __init__(self, fget, finit=None, doc=None):
        self.fget = fget
        self.finit = finit
        if fget is not None:
            self.__name = fget.__name__
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self.finalized = False
        
    def __get__(self, obj, objtype=None):    
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(u"Can't get attribute: no getter was given")
        return self.fget(obj)
    
    def __set__(self, obj, value):
        if self.finit is None:
            raise AttributeError(u"Can't initialize attribute: no init for attribute was given")
        lock_name = "__prop_%s_locked" % self.__name
        if not getattr(obj, lock_name, False):
            self.finit(obj, value)
            setattr(obj, lock_name, True)
        elif self.fget(obj) is not value:
            raise TypeError(u"immutable property %s of %s can't be modifyed" % (self.__name, obj))
        
    def __delete__(self, obj):
        raise TypeError(u"immutable property %s of %s can't be deleted" % (self.__name, obj))
    
    def getter(self, fget):
        return type(self)(fget, self.finit, self.__doc__)

    def init(self, finit):
        return type(self)(self.fget, finit, self.__doc__)

