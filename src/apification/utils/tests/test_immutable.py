from apification.utils import immutable

def build_class1():
    class A(object):
        @immutable
        def x(self):
            return self._x
        
        @x.init
        def x(self, value):
             self._x = value
    return A

def build_class2():
    class A(object):
        def x(self):
            return self._x
        
        def initx(self, value):
            self._x = value
        x = immutable(x, initx)
    return A


def test_immutable_constructor1():
    e = None
    v = 42
    try:
        A = build_class1()
        a = A()
        a.x = v
        assert a.x == v
    except Exception as e:
        raise e
        pass            
    assert e is None
    

def test_immutable_constructor2():
    e = None
    v = 108
    try:
        A = build_class2()
        a = A()
        a.x = v
        assert a.x == v
    except Exception as e:
        raise e
    assert e is None

def test_immutable_immutability():
    e = None
    A = build_class1()
    a = A()
    a.x = 1
    try:
        a.x = 2
    except TypeError as e:
        pass
    assert isinstance(e, TypeError)

def test_immutable_is_undelitable():
    e = None
    A = build_class2()
    a = A()
    a.x = 1
    try:
        del a.x
    except TypeError as e:
        pass
    assert isinstance(e, TypeError)