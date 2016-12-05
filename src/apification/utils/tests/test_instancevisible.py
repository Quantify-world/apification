from apification.utils.instancevisible import instancevisible


def test_instancevisible():
    class M(instancevisible.Meta):
        a = 1

        @instancevisible
        def f(cls):
            return cls.a
    
    class A(object):
        __metaclass__ = M
        
        a = 2
        
        def __init__(self):
            self.a = 3

    i = A()

    assert i.f() == A.f() == 2
    assert isinstance(M.f, instancevisible)


def test_instancevisible_metaclass_inheritance():
    class M(instancevisible.Meta):
        a = 1

        @instancevisible
        def f(cls):
            return cls.a
    
    class M2(M):
        pass

        __metaclass__ = M2
        
        a = 2
        
        def __init__(self):
            self.a = 3

    i = A()

    assert i.f() == A.f() == 2
    assert isinstance(M.f, instancevisible)


def test_instancevisible_class_inheritance():
    class M(instancevisible.Meta):
        a = 1

        @instancevisible
        def f(cls):
            return cls.a
    
    class A(object):
        __metaclass__ = M
        
        a = 2
        
        def __init__(self):
            self.a = 3

    class A2(A):
        pass

    i = A2()

    assert i.f() == A2.f() == 2
    assert isinstance(M.f, instancevisible)


def test_instancevisible_override():
    class M(instancevisible.Meta):
        a = 1

        @instancevisible
        def f(cls):
            return cls.a
    
    class A(object):
        __metaclass__ = M
        
        a = 2
        
        def __init__(self):
            self.a = 3

    class A2(A):
        @classmethod
        def f(cls):
            return 4

    i = A2()

    assert i.f() == A2.f() == 4
    assert isinstance(M.f, instancevisible)
