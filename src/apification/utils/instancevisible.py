class InstanceVisibleMeta(type):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name, None)
            if isinstance(attr_value, instancevisible):
                cls_dict[attr_name] = classmethod(attr_value.method)
        return super(InstanceVisibleMeta, cls).__new__(cls, cls_name, cls_parents, cls_dict)            


class instancevisible(object):
    """
        Converts a metaclass-defined function to classmethod.

        >>> class Metaclass(instancevisible.Meta):
        ...     @instancevisible
        ...     def func(cls):
        ...         return cls.__name__
        ...     
        >>> class A(object):
        ...     __metaclass__ = Metaclass
        ... 
        >>> obj = A()
        >>> obj.func()
        'A'
        >>> A.func()
        'A'
    """
    Meta = InstanceVisibleMeta

    def __init__(self, method):
        self.method = method

    def __get__(self, instance, owner):
        return self
