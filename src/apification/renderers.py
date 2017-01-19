import json

class JSONRenderer(object):
    def render(self, data):
        return json.dumps(data)
