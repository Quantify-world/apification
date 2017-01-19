import inspect
import warnings

from types import MethodType


SELF_WARN_MESSAGE = """"self" found as first argument for %(method)s method of class %(cls)s.

This class will not be instantiated, so you shouldn't use keyword "self" because this class
will never have any instance method (use "cls" instead).

If you're sure you want to use "self" regardless of traditional naming conventions add
    ...
    __allow_self_as_first_arg__ = True
    ...
to class %(cls)s declaration to suppress this warning."""


      
class NoninstantiableMeta(type):
    def _prevent_instantiating(cls, *args, **kwargs):
        raise TypeError('%s must not be instantiated' % cls)
        
    def __new__(cls, cls_name, cls_parents, cls_dict):
        ret = super(NoninstantiableMeta,cls).__new__(cls, cls_name, cls_parents, cls_dict)
        for name in dir(ret):
            value = getattr(ret, name)
            if isinstance(value, MethodType):  
                if not getattr(ret, '_allow_self_as_first_arg', False) and 'self' in inspect.getargs(value.func_code).args[:1]:
                    warn_message = SELF_WARN_MESSAGE % {'cls': cls_name, 'method': name}
                    warnings.warn(warn_message, SyntaxWarning)
                new_method = classmethod(value.im_func)
                setattr(ret, name, new_method) # turn all methods to classmethods
        ret.__init__ = classmethod(cls._prevent_instantiating)  # You shall not pass!
        ret.__new__ = classmethod(cls._prevent_instantiating)  # You shall not pass!
        return ret
    

class Noninstantiable(object):
    __metaclass__ = NoninstantiableMeta

