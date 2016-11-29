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
        from django.core.serializers import register_serializer, serialize
        from django.db.models import Model

        if not isinstance(instance, Model):
            raise SkipBackend()

        register_serializer('bluedata', 'apification.utils.django_serializer')
        
        fake_qs = instance.__class__.objects.none()
        fake_qs.result_cache = [instance]
        return serialize("bluedata", fake_qs)[0]


class AllAttributesBackend(BaseSerializerBackend):
    @classmethod
    def run(cls, instance):
        if not hasattr(instance, '__dict__'):
            raise SkipBackend()
        ret = {}
        for k, v in instance.__dict__.iteritems():
            if not isinstance(v, (int, long, float)):
                ret[k] = unicode(v)
        return ret
