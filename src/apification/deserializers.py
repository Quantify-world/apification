class Deserializer(object):
    def __init__(self, action):
        self.action = action
    
    def run(self):
        parser = self.get_parser()
        data = parser.parse(self.action.request.body)
        return self.to_object(data)

    def get_parser(self):
        # TODO: backend system
        from apification.parsers import JSONParser
        return JSONParser()

    def to_object(self, data):
        raise NotImplementedError()
