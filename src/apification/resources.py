from apification.nodes import ApiBranch


class Resource(ApiBranch):
    def get_object(self):
        raise NotImplementedError()

class DjangoResource(Resource):
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs[self.get_url_argument_name()])
