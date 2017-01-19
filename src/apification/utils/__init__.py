from apification.utils.noninstantiable import Noninstantiable, NoninstantiableMeta
from apification.utils.writeonce import writeonce
from apification.utils.instancevisible import instancevisible


__all__ = ['Noninstantiable', 'NoninstantiableMeta', 'writeonce', 'instancevisible', 'issubclass_safe']

def issubclass_safe(C, B):
    try:
        return issubclass(C, B)
    except TypeError:
        return False
