from ping_project.api import Hosts, HostSerializer
from apification.utils import Noninstantable

def test_parent_class():
    assert Hosts.Host.Get.parent_class == Hosts.Host

def test_serializer_resolve():
    assert Hosts.Host.Get.serializer == HostSerializer

def test_collectible_resolve():
    assert Hosts.get_collectible_class() == Hosts.Host

def test_params():
    assert len(Hosts.Host.Get.get_params()) == 2

def test_noninstable():
    e, o  = None, None
    try:
        o = Noninstantable()
    except TypeError as e:  pass
    assert o is None
    assert isinstance(e, TypeError)

def test_noninstable_keyword_self_check():
    C = None
    try:
        class C(Noninstantable):
            def func(self, a, b=1):
                pass
    except TypeError as e: pass
    assert C is None
    
    class C(Noninstantable):
            def func(cls, self, b=1):  # self as non first argument is allowed for whatever reasons
                pass
    assert issubclass(C, Noninstantable)

def test_noninstable_keyword_self_check_suppression():
    C = None
    class C(Noninstantable):
        __allow_firstarg_self__ = True
        def func(self, a, b=1):
            pass
    assert issubclass(C, Noninstantable)
