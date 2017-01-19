from apification.exceptions import ApiStructureError
from apification.resources import Resource
from apification.actions import Action


def resource(klass):
    klass._decorated = True
    return klass


def action(klass):
    klass._decorated = True
    return klass


def serializer(klass):
    klass._decorated = True
    return klass
