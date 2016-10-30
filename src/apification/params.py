from django.http import HttpRequest

from apification.exceptions import InvalideParamError, MissingParamError


class ParamMetaclass(type):
    def __unicode__(cls):
        return u'Param %s' % cls.__name__.lower()


class Param(object):
    node = None
    required = True

    def __init__(self):
        raise TypeError(u'Params could not be instantiated')

    @classmethod
    def construct(cls, node_class, request, args, kwargs):
        raise NotImplementedError()

    @classmethod
    def is_valid(cls, node_class, value):
        if value is None:
            cls.check_for_none(node_class)
        cls.check_value(node_class, value)

    @classmethod
    def check_value(cls, node_class, value):
        raise NotImplementedError()

    @classmethod
    def check_for_none(cls, node_class):
        if cls.required:
            raise MissingParamError('%s is required' % cls)  # TODO: get param name


class PathParam(Param):   # base class for fetch params from url
    @classmethod
    def get_path(cls):
        raise NotImplementedError()


class PkParam(PathParam):
    @classmethod
    def construct(cls, node_class, request, args, kwargs):
        return kwargs[node_class.get_url_argument_name()]

    @classmethod
    def is_valid(cls, node_class, value):
        try:
            int(value)
        except (TypeError, ValueError):
            raise InvalideParamError('Primary key value must be integer, not %s' % (type(value)))

    @classmethod
    def get_path(cls, node_class):
        return r'(?P<%s>\d+)/' % node_class.get_url_argument_name()


class RequestParam(Param):
    @classmethod
    def construct(cls, node_class, request, args, kwargs):
        return request

    @classmethod
    def is_valid(cls, node_class, value):
        if not isinstance(value, HttpRequest):
            raise InvalideParamError()


class UserParam(Param):
    @classmethod
    def construct(cls, node_class, request, args, kwargs):
        return request.user

    @classmethod
    def is_valid(cls, node_class, value):
        from django.contib.auth import get_user_model

        if not isinstance(value, get_user_model()):
            raise InvalideParamError()
