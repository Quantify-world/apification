from apification.nodes import ApiBranch
from apification.params import PkParam
from apification.exceptions import ApiStructureError
from apification.resources import Resource


class Collection(ApiBranch):
    collectible_child = None  # name of child class which will represent single item of collection

    def __iter__(self):
        return self.iter_collectible_nodes()

    def get_list(self):
        raise NotImplementedError()

    def get_object(self):
        return self.get_list()

    @classmethod
    def get_collectible_class(cls):
        if cls.collectible_child is not None:  # collectible child specified
            return getattr(cls, cls.collectible_child)
        
        collectible_class = None
        for attr_name, node_class in cls.iter_children():
            if issubclass(node_class, Collectible):
                if collectible_class is not None:
                    raise ApiStructureError(
                        u'Multiple collectable classes in collection %s. Specify "collectible_child" attribute in collection.' % cls)
                collectible_class = node_class
        if collectible_class is None:
            raise ApiStructureError(u'No collectable classes specified in collection %s' % cls)
        return collectible_class

    @classmethod
    def get_collectible_pk_param(cls):
        # not over all params including inherited from parent nodes but only over personal
        for param_name, param_class in cls.get_collectible_class().get_local_params().iteritems():
            if issubclass(param_class, PkParam):
                return param_name, param_class
        raise ApiStructureError(u'Could not found PkParam in collectible %s for collection %s' % (cls.get_collectible_class(), cls))

    def iter_collectible_nodes(self):
        collectible_class = self.get_collectible_class()
        param_name, param_class = self.get_collectible_pk_param()
        for obj in self.get_list():
            param_values = self.param_values.copy()
            param_values[param_name] = obj.pk
            node = collectible_class(param_values)
            yield node


class DjangoCollection(Collection):
    pass


class Collectible(Resource):
    resource_param = PkParam

    @classmethod
    def get_url_argument_name(cls):
        return '%s_pk' % cls.name

    @classmethod
    def get_path(cls):
        return cls.resource_param.get_path(cls)
    
    @classmethod
    def get_local_params(cls):
        params = super(Collectible, cls).get_local_params()
        params[cls.get_url_argument_name()] = cls.resource_param
        return params

    # TODO: decouple django-related stuff
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.param_values[self.get_url_argument_name()])
