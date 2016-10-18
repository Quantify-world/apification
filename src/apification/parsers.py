from apification.utils.http import parse_http_accept


class BaseParser(object):
    pass


class JSONParser(BaseParser):
    formats = ['application/json', 'text/json']

    def accept_format(self, request):
        for format in self.formats:
            if format in parse_http_accept(request.META['HTTP_ACCEPT']):
                return True
