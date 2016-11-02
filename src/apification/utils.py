from types import FunctionType

      
class NoninstantableMeta(type):
    def __prevent_instantiating__(*args, **kwargs):
        raise TypeError('%s must not be instantiated' % args[0])
        #  TODO: raise custom exception?
        
    def __new__(cls, cls_name, cls_parents, cls_dict):
        for name, value in cls_dict.iteritems():
            if isinstance(value, FunctionType):  
                if not cls_dict.get('__allow_firstarg_self__', False) and 'self' in inspect.getargs(value.func_code).args[:1]:
                    error_text  = '"self" found as first argument for %s method of class %s. \nThis class will not be instantiated,' % (name, cls_name)
                    error_text += ' so you shouldn\'t use keyword "self" because this class will never have any instance method (use "cls" instead).'
                    error_text += '\nIf you\'re sure you want to use "self" regardless of traditional naming conventions '
                    error_text += 'add \n\t...\n\t__allow_firstarg_self__ = True\n\t...\n to class %s declaration to suppress this error.' % cls_name
                    raise TypeError(error_text)
                cls_dict[name] = classmethod(value)  # turn all methods to classmethods
        ret = super(NoninstantableMeta,cls).__new__(cls, cls_name, cls_parents, cls_dict)
        ret.__init__ = classmethod(cls.__prevent_instantiating__)  # You shall not pass!
        return ret
    

class Noninstantable(object):
    __metaclass__ = NoninstantableMeta
    
