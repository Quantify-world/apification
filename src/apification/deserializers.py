class DeserializerMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(DeserializerMetaclass, cls).__new__(name, parents, dct)
        return ret
        

class Deserializer(object):
    def __init__(self, node, action):
        from apification.actions import Action
        from apification.nodes import ApiNode

        assert isinstance(action, Action)
        self.action = action

        assert issubclass(node, ApiNode)
        self.node = node

    @classmethod
    def get_model(cls):
        return cls.node.model

    def to_object(self):
        kwargs = {}
        for name, value in self.iter_children():
            kwargs['name'] = 1  # value().to_object()
        return self.construct_instance(**kwargs)

    def construct_instance(self, **kwargs):
        return self.node.model(**kwargs)
        # obj = self.node.model()
        # for k, v in kwargs.items():
        #     setattr(obj, k, v)
        # return obj
    
    def run(self):
        parser = self.get_parser()
        data = parser.parse(self.action.request.body)
        return self.to_object(data)

    @classmethod
    def iter_children(cls):
        for attr_name in dir(cls):
            if (isinstance(getattr(type(cls), attr_name, None), property)):  # prevent accesing properties
                continue

            node = getattr(cls, attr_name)
            if (type(node) is cls.__metaclass__ and not attr_name.startswith('_')):
                yield attr_name, node

    def get_parser(self):
        # TODO: backend system
        from apification.parsers import JSONParser
        return JSONParser()
