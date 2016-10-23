def Deserializer(object):
    def __init__(self, action):
        self.action = action
    
    def run(self):
        parser = self.get_parser()
        data = parser.parse(self.action.request.body)
        return self.from_parser(data)

    def get_parser(self):
        # TODO: backend system
        from apification.parsers import JSONParser
        return JSONParser()

    def from_parser(self, data):
        raise NotImplementedError()

