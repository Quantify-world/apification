class NotDefined:
    pass


def has_descent_attrs(obj, *args):
    i = obj
    for attr_name in args:
        if not hasattr(i, attr_name):
            return False
        i = getattr(i, attr_name)
    return True


def get_descent_attrs(obj, *args, **kwargs):
    default = kwargs.pop('default', NotDefined)
    i = obj
    for attr_name in args:
        if not hasattr(i, attr_name):
            if default is NotDefined:
                raise AttributeError(attr_name)
            else:
                return default
        i = getattr(i, attr_name)
    return i
