from django.http import HttpResponse

class Serializer(object):
    def __init__(self, action, obj):
        self.action = action
        self.obj = obj
        
    def run(self):
        renderer = self.get_renderer()
        data = self.from_object()
        return HttpResponse(renderer.render(data))  # TODO: may be move Response-wrapping to Renderer
    
    def get_renderer(self):
        from apification.renderers import JSONRenderer
        return JSONRenderer()
    
    def from_object(self):
        raise NotImplementedError()