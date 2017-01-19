from apification.nodes import ApiBranch
from apification.exceptions import ApiStructureError
from apification.resources import Resource
from apification.utils import tpath


class Collection(Resource):
    collectible = './Item'  # tpath of child class which will represent single item of collection

    def __iter__(self):
        return self.iter_collectible_nodes()

    @classmethod
    def get_collectible_class(cls):
        try:
            collectible = tpath.parse(cls, cls.collectible)[0]
            assert issubclass(collectible, Collectible)
        except (tpath.TPathError, IndexError) as e:
            raise ApiStructureError(u'Unable to find collectible on path "%s" for collection %s: %s' % (cls.collectible, cls, e))
        return collectible

    def iter_collectible_nodes(self):
        collectible_class = self.get_collectible_class()
        for obj in self.get_list():
            node = collectible_class(request=self.request, args=self.args, kwargs=self.kwargs, instance=obj)
            yield node

    def get_queryset(self):
        raise NotImplementedError()

    def make_instance(self):
        return self.get_queryset()


class Collectible(Resource):
    collection = '..'

    @classmethod
    def get_collection_class(cls):
        try:
            collection = tpath.parse(cls, cls.collection)[0]
            assert issubclass(collection, Collection)
        except (tpath.TPathError, IndexError) as e:
            raise ApiStructureError(u'Unable to find collection path "%s" for collectible %s: %s' % (cls.collection, cls, e))
        return collection

    @classmethod
    def get_url_argument_name(cls):
        return '%s_pk' % cls.name

    @classmethod
    def get_path(cls):
        return u'/(?P<%s>\d+)/' % cls.get_url_argument_name()

    # TODO: decouple django-related stuff
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.param_values[self.get_url_argument_name()])
