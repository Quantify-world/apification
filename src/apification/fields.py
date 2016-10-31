from apification.serializers import Serializer

class Field(Serializer):
    @classmethod
    def from_object(cls, obj, **kwargs):
        value = getattr(obj, cls.name)
        return value


class IntField(Field):
    pass


class TextField(Field):
    pass
