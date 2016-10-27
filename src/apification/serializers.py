from django.http import HttpResponse

class SerializerMetaclass(type):
    def __new__(cls, name, parents, dct):
        ret = super(SerializerMetaclass, cls).__new__(cls, name, parents, dct)
        return ret

class Serializer(object):
    def __init__(self, node, action, obj):
        self.action = action
        self.obj = obj
        self.node = node
        
    def run(self):
        renderer = self.get_renderer()
        data = self.from_object()
        return HttpResponse(renderer.render(data))  # TODO: may be move Response-wrapping to Renderer
    
    def get_renderer(self):
        from apification.renderers import JSONRenderer
        return JSONRenderer()
    
    def from_object(self):
        raise NotImplementedError()