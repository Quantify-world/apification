import warnings
from apification.utils import Noninstantiable, NoninstantiableMeta



def test_noninstantiable():
    e, o  = None, None
    try:
        o = Noninstantiable()
    except TypeError as e:  pass
    assert o is None
    assert isinstance(e, TypeError)

def test_noninstantiable_keyword_self_check_invalid():
    with warnings.catch_warnings(record=True) as w:
        class C(Noninstantiable):
            def func(self, a, b=1):
                pass
    assert len(w) == 1
    assert issubclass(w[0].category, SyntaxWarning)
    assert issubclass(C, Noninstantiable)
    
def test_noninstantiable_keyword_self_check_valid():
    C = None
    with warnings.catch_warnings(record=True) as w:
        class C(Noninstantiable):
            def func(cls, self, b=1):  # self as non first argument is allowed for whatever reasons
                pass
    assert not w
    assert issubclass(C, Noninstantiable)

def test_noninstantiable_classmethods():
    class A(Noninstantiable):
        def a(cls):
            return cls
    assert A.a() is A

def test_noninstantiable_keyword_self_check_suppression():
    C = None
    class C(Noninstantiable):
        _allow_self_as_first_arg = True
        def func(self, a, b=1):
            pass
    assert issubclass(C, Noninstantiable)


def test_noninstantable_inheritance():
    class A(object):
        _allow_self_as_first_arg = True
    e = None
    try:
        class B(A):
            __metaclass__ = NoninstantiableMeta
            def a(self):
                pass
    except TypeError as e:
        pass
    assert e is None
    