from apification.nodes import ApiNode
from apification.utils import tpath


class A(ApiNode):
    class B1(ApiNode):
        class C(ApiNode):
            pass
    class B2(ApiNode):
        class C(ApiNode):
            class D(ApiNode):
                class A(ApiNode):
                    pass


def test_tpath_forward():
    result = tpath.parse(A.B2, '/.//')
    print 'Res:', result
    
    # assert len(result) == 1
    # assert result[0] == A

test_tpath_forward()
