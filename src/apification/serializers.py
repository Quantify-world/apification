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
        
    def run(self):
        renderer = self.get_renderer()
        data = self.from_object()
        return HttpResponse(renderer.render(data))  # TODO: may be move Response-wrapping to Renderer
    
    def get_renderer(self):
        from apification.renderers import JSONRenderer
        return JSONRenderer()
    
    def from_object(self):
        raise NotImplementedError()  # self.node.get_object()


class ListSerializer(Serializer):
    serializer_name = 'default_serializer'
    def from_object(self):
        ret = []
        for node in self.iter_nodes():
            serializer = node.get_serializer(serializer_name=self.serializer_name)
            data = serializer.run(node.get_object())
            ret.append(data)
        return ret
