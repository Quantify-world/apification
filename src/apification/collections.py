from apification.nodes import ApiBranch


class Collection(ApiBranch):
    @classmethod
    def get_path(cls):
        return cls.name + '/'


class DjangoCollection(Collection):
    pass
