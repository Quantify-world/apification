from apification.nodes import ApiNode


class Collection(ApiNode):
    @classmethod
    def get_path(cls):
        return cls.name + '/'


class DjangoCollection(Collection):
    pass
