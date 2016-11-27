from pytest import raises
import warnings

from apification.utils import writeonce



def test_writeonce_constructor():
    class A(object):
        x = writeonce()
    v = 42
    a = A()
    a.x = v
    assert a.x == v


def test_writeonce_writes_only_once():
    class A(object):
        x = writeonce()
    a = A()
    a.x = 1
    with raises(TypeError):
        a.x = 2


def test_writeonce_is_undelitable():
    class A(object):
        x = writeonce()
    a = A()
    a.x = 1
    with raises(TypeError):
        del a.x

def test_default():
    default = 'some_default_value'
    class A(object):
        x = writeonce(default)

    a = A()
    assert a.x is default
    a.x = 1
    with raises(TypeError):
        del a.x

def test_no_default():
    class A(object):
        x = writeonce()
        
    a = A()
    with raises(AttributeError):
        a.x

def test_metaclass():
    class M(type):
        x = writeonce()

    class A(object):
        __metaclass__ = M

    A.x = 1
    with raises(TypeError):
        A.x = 2
    assert A.x == 1

def test_classdecorator():
    @writeonce('x', 'y')
    class A(object):
        pass

    a = A()
    a.x = 1
    assert a.x == 1
    a.y = 2
    assert a.y == 2
    
    with raises(TypeError):
        a.y = 4
 

def test_inheritance():
    class A(object):
        x = writeonce()
    
    class B(A):
        pass
    
    b = B()
    b.x = 1
    assert b.x == 1
    with raises(TypeError):
        b.x = 4

def test_overwrite_same_warning():
    class A(object):
        x = writeonce()

    a = A()
    a.x = 1
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        a.x = 1
    assert len(w) == 1
    assert issubclass(w[0].category, UserWarning)

def test_custom_message():
    class A(object):
        x = writeonce(writeonce_msg='qwe-%(name)s-%(instance)s-%(value)s-%(old_value)s')

        def __str__(self):
            return 'a'

    a = A()
    a.x = 1
    with raises(TypeError) as e:
        a.x = 2
    assert e.value.message == 'qwe-x-a-2-1'

def test_inheritance_with_override():
    class A(object):
        x = 1
    
    class B(A):
        x = writeonce()  # explicit override - so it's ok
    
    b = B()
    b.x = 1
    assert b.x == 1
    with raises(TypeError):
        b.x = 4
        
def test_inheritance_classdecorator_with_override():
    class A(object):
        x = 1
    
    with raises(TypeError):
        @writeonce('x')  # implicit - not ok
        class B(A):
            pass


def test_inheritance_with_classdecorator():
    @writeonce('x','y')
    class B(object):
        pass
    
    class A(B):
        pass
    
    a = A()
    a.x = 1
    assert a.x == 1
    a.y = 2
    assert a.y == 2
    
    with raises(TypeError):
        a.y = 4
    

def test_set_in_classdecorator_cant_be_redefined():
    with raises(TypeError):
        @writeonce('x','y')
        class B(object):
            x = 5

def test_classdecorator_default_value():
    val = 'some_default'
    @writeonce(x=val)
    class A(object):
        pass
    a = A()
    assert a.x is val
    a.x = 1
    assert a.x is 1
    with raises(TypeError):
        a.x = 2


def test_metaclass_decorator():
    @writeonce('x', 'y')
    class M(type):
        pass
    
    class A(object):
        __metaclass__ = M
    
    class B(A):
        pass
    
    A.x = 1
    assert A.x is 1
    with raises(TypeError):
        A.x = 2

    with raises(AttributeError):
        B.x

def test_metaclass_decorator_inheritance():
    @writeonce('x',y=123)
    class M1(type):
        pass
    
    class M2(M1):
        pass
    
    class A(object):
        __metaclass__ = M2

    A.x = 1
    assert A.x is 1
    assert A.y is 123
    with raises(TypeError):
        A.x = 2