class instancevisible(object):
    def __init__(self, method):
        self.method = classmethod(method)

    def __get__(self, instance, owner):
        if issubclass(owner, InstanceVisibleMeta):
            return self
        return self.method.__get__(instance, owner)


class InstanceVisibleMeta(type):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        for attr_name in dir(cls):
            attr_value = getattr(cls, attr_name, None)
            if isinstance(attr_value, instancevisible):
                cls_dict[attr_name] = attr_value
        return super(InstanceVisibleMeta, cls).__new__(cls, cls_name, cls_parents, cls_dict)            
