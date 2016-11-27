from apification.backends import BaseBackend, SkipBackend


class BaseSerializerBackend(BaseBackend):
    registry_name = 'serializer'

    @classmethod
    def run(cls, instance):
        raise NotImplementedError()


class ToJsonSerializerBackend(BaseSerializerBackend):
    method_name = 'to_json'

    @classmethod
    def run(cls, instance):
        if hasattr(instance, cls.method_name):
            return getattr(instance, cls.method_name)()
        else:
            raise SkipBackend()

#TODO: testing required
class DjangoSerializerBackend(BaseSerializerBackend):
    @classmethod
    def run(cls, instance):
        from django.core.serializers.base import register_serializer
        from django.core.serializers import serialize

        register_serializer('bluedata', 'apification.utils.django_serializer')
        
        return serialize("bluedata", [instance])[0]


class AllAttributesBackend(BaseSerializerBackend):
    pass


class Serilializer:
    backends = AllAttributesBackend + ToJsonSerializerBackend
