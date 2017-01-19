from apification.resources import Resource

from apification import resource


@resource
class A(Resource):
    @resource
    class B(Resource):
        pass
    
@resource
class C(A):
    pass


def test_node_children_inheritance():
    assert 'B' not in C.children
