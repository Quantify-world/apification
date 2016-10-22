from apification.nodes import ApiNode


class Resource(ApiNode):
    name = None

    @classmethod
    def get_path(cls):
        return r'(?P<pk>\d+)/'

    @classmethod
    def get_view(cls, action):
        action_class = getattr(cls, action)
        def view(request, *args, **kwargs):
            action = action_class(request, args=args, kwargs=kwargs)
            return action.run()
        return view


class DjangoResource(Resource):
    def get_queryset(self):
        if self.parent is None:
            raise NotImplementedError()
        return self.parent.get_queryset()

    def get_object(self):
        return self.get_queryset().get(pk=self.kwargs['pk'])
