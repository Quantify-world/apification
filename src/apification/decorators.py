from apification.exceptions import ApiStructureError
from apification.utils import issubclass_safe


class Index:
    """Used for store registered classes order defined in code by enumerating"""
    def __init__(self):
        self.value = 0

    def inc(self):
        self.value += 1
        return self.value

index = Index()


def resource(klass):
    from apification.resources import Resource

    klass._decorated = resource.func_name
    klass._index = index.inc()
    if not issubclass_safe(klass, Resource):
        raise ApiStructureError(u'%s is not a Resource subclass. Use @resource decorator to register child resources' % klass)
    return klass


def action(klass):
    from apification.actions import Action

    klass._decorated = action.func_name
    klass._index = index.inc()
    if not issubclass_safe(klass, Action):
        raise ApiStructureError(u'%s is not an Action subclass. Use @action decorator to register actions within resource' % klass)
    return klass


def serializer(klass):
    from apification.serializers import Serializer

    klass._decorated = serializer.func_name
    klass._index = index.inc()
    if not issubclass_safe(klass, Serializer):
        raise ApiStructureError(u'%s is not an Serializer subclass. Use @serializer decorator to register serializers for resource' % klass)
    return klass
