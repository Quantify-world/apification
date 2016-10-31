from django.conf.urls import url

from apification import api_settings
from apification.nodes import ApiLeaf


class Action(ApiLeaf):
    method = 'GET'  # default http method
    serializer = 'default_serializer'
    deserializer = 'default_deserializer'

    @classmethod
    def get_method_and_name(cls):
        if cls.get_name().upper() in api_settings.VALID_HTTP_METHODS:
            return cls.get_name(), ''
        else:
            return cls.method, '%s/' % cls.get_name()

    @classmethod
    def prepare_serializers(cls):
        from apification.serializers import Serializer

        if isinstance(cls.serializer, type) and issubclass(cls.serializer, Serializer):
            cls.serializer.node_class = cls  # set serializer context
        else:  # string
            cls._serializers_preparations = [(cls.serializer, {cls: 'serializer'})]

    @classmethod
    def get_urls(cls):
        method, action_name = cls.get_method_and_name()
        path = r'%s%s$' % (cls.parent_class.construct_path(), action_name)

        return [url(path, cls.parent_class.entrypoint, name='%s-%s' % (cls.parent_class.get_name(), cls.get_name()))]

    def process(self, obj):
        return obj

    def run(self):
        obj = self.parent.get_object()
        obj = self.process(obj)
        data = self.serialize(obj, serializer_name='serializer')
        return self.render(data)

    def get_deserializer(self):
        pass


class PayloadAction(Action):
    method = 'POST'

    def deserialize(self):
        pass
    #     node = self
    #     while not node.deserializer_class:
    #         node = node.parent
    #     
    #     if node.deserializer_class:    
    #         return node.deserializer_class(action=self)
    #     else:
    #         raise ImproperlyConfigured("deserializer_class set nowhere from %s to %s" % (self, node))
        
    def run(self):
        obj = self.deserialize()
        obj = self.process(obj)
        data = self.serialize(obj, serializer_name='serializer')
        return self.render(data)
