from django.conf.urls import url

from apification.nodes import ApiNode
from apification import api_settings


class Action(ApiNode):
    method = 'GET'  # default http method
    name = None

    @classmethod
    def get_name(cls):
        return cls.name or cls.__name__.lower()
        

    @classmethod
    def get_method_and_name(cls):
        if cls.get_name() in api_settings.VALID_HTTP_METHODS:
            return cls.get_name(), ''
        else:
            return cls.method, '%s/' % cls.get_name()
    
    @classmethod
    def url_entry(cls):
        parent_path = cls.parent.get_path()
        method, action_name = cls.get_method_and_name()
        return url(r'%s%s$' % (parent_path, action_name),
                   cls.parent.get_view(method=method),
                   name='%s-%s' % (cls.parent.name, cls.get_name()))
