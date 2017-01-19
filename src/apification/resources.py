from apification.nodes import ApiBranch


class Resource(ApiBranch):
    def get_object(self):
        raise NotImplementedError()
