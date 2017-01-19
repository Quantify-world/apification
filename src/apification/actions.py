from django.conf.urls import url

from apification import api_settings
from apification.nodes import ApiLeaf, SerializerBail


class Action(ApiLeaf):
    method = 'GET'  # default http method
    serializer = 'default_serializer'
    deserializer = 'default_deserializer'

    @classmethod
    def prepare_serializers(cls):
        from apification.serializers import Serializer

        if isinstance(cls.serializer, type) and issubclass(cls.serializer, Serializer):
            cls.serializer.node_class = cls  # set serializer context
        elif isinstance(cls.serializer, basestring):  # string
            SerializerBail(cls).init_action()
        else:
            pass  # TODO: raise warning

    @classmethod
    def get_suffix(cls):
        if hasattr(cls, 'suffix'):
            return u'%s/' % cls.suffix.rstrip('/')
        if cls.name.upper() in api_settings.VALID_HTTP_METHODS:
            return ''
        else:
            return '%s/' % cls.name.lower()

    @classmethod
    def get_view_name(cls):
        if hasattr(cls, 'view_name'):
            return cls.view_name
        return '%s-%s' % (cls.parent_class.name.lower(), cls.name.lower())

    @classmethod
    def get_urls(cls):
        path = r'%s%s$' % (cls.parent_class.construct_path(), cls.get_suffix())

        return [url(path, cls.parent_class.entrypoint, name=cls.get_view_name())]

    def process(self, node):
        return node

    def run(self):
        node = self.parent
        node = self.process(node)
        data = node.serialize(serializer=self.serializer)
        return self.render(data)

    def get_deserializer(self):
        pass


class PayloadAction(Action):
    method = 'POST'

    def deserialize(self):
        pass
        
    def run(self):
        obj = self.deserialize()
        node = self.parent_class(self.request, self.args, self.kwargs, instance=obj)
        node = self.process(node)
        data = self.serialize(obj, serializer_name='serializer')
        return self.render(data)
