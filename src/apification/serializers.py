from django.http import HttpResponse


# class SerializerMetaclass(type):
#     def __new__(cls, name, parents, dct):
#         ret = super(SerializerMetaclass, cls).__new__(cls, name, parents, dct)
#         return ret


class Serializer(object):
    node_class = None

    def __init__(self, node):
        assert isinstance(node, self.node_class)
        self.node = node
        
    def run(self, obj):
        renderer = self.get_renderer()
        data = self.from_object(obj)
        return HttpResponse(renderer.render(data))  # TODO: may be move Response-wrapping to Renderer
    
    def get_renderer(self):
        from apification.renderers import JSONRenderer
        return JSONRenderer()
    
    def from_object(self, obj):
        raise NotImplementedError()


class ListSerializer(Serializer):
    serializer_name = 'default_serializer'
    def from_object(self, obj):
        ret = []
        for node in self.iter_nodes():
            serializer = node.get_serializer(serializer_name=self.serializer_name)
            data = serializer.from_object(node.get_object())
            ret.append(data)
        return ret
