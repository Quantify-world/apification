import json

from apification.utils.http import parse_http_accept


class ParsingError(Exception):
    pass


class BaseParser(object):
    def parse(self, data):
        raise NotImplementedError()


class JSONParser(BaseParser):
    formats = ['application/json', 'text/json']

    def accept_format(self, request):
        for format in self.formats:
            if format in parse_http_accept(request.META['HTTP_ACCEPT']):
                return True
    
    def parse(self, data):
        try:
            return json.loads(data)
        except ValueError:
            raise ParsingError()
