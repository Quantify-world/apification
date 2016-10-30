from apification.nodes import ApiBranch
from apification.params import PkParam
from apification.exceptions import ApiStructureError


class Collection(ApiBranch):
    collectible_child = 'Item'  # name of child class which will represent single item of collection

    @classmethod
    def get_path(cls):
        return cls.name + '/'

    def __iter__(self):
        return self.iter_collectible_nodes()

    def get_list(self):
        raise NotImplementedError()

    @classmethod
    def get_collectible_class(cls):
        return getattr(cls, cls.collectible_child)

    @classmethod
    def get_collectible_pk_param(cls):
        # not over all params including inherited from parent nodes but only over personal
        for param_name, param_class in cls.get_collectible_class().params.iteriterms():
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
