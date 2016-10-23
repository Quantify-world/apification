from apification.nodes import ApiBranch


class Resource(ApiBranch):
    @classmethod
    def get_url_argument_name(cls):
        return '%s_pk' % cls.name

    @classmethod
    def get_path(cls):
        return r'(?P<%s>\d+)/' % cls.get_url_argument_name()
        

class DjangoResource(Resource):
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs[self.get_url_argument_name()])
