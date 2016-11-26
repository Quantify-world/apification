from django.conf.urls import url

from apification import api_settings
from apification.nodes import ApiLeaf, SerializerBail


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
        elif isinstance(cls.serializer, basestring):  # string
            SerializerBail(cls).init_action()
                # [(cls.serializer, {cls: 'serializer'})]
        else:
            pass  # TODO: raise warning

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
        
    def run(self):
        obj = self.deserialize()
        obj = self.process(obj)
        data = self.serialize(obj, serializer_name='serializer')
        return self.render(data)
