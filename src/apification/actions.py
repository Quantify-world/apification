from django.conf.urls import url

from apification import api_settings
from apification.nodes import ApiLeaf


class Action(ApiLeaf):
    method = 'GET'  # default http method

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
    def get_urls(cls):
        method, action_name = cls.get_method_and_name()
        path = r'%s%s$' % (cls.parent.construct_path(), action_name)
        
        return [url(path, cls.parent.view, name='%s-%s' % (cls.parent.name, cls.get_name()))]

    def run(self):
        pass