from apification.nodes import ApiBranch


class Collection(ApiBranch):
    collectible_child = 'Item'

    @classmethod
    def get_path(cls):
        return cls.name + '/'


class DjangoCollection(Collection):
    pass
