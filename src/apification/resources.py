from apification.nodes import ApiBranch


class Resource(ApiBranch):
    name = None

    @classmethod
    def get_path(cls):
        return r'(?P<pk>\d+)/'


class DjangoResource(Resource):
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])
