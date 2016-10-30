class ApiStructureError(Exception):
    pass


class NodeParamError(TypeError):
    pass


class InvalideParamError(NodeParamError):
    pass


class MissingParamError(NodeParamError):
    pass
