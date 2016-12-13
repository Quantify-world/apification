from apification.nodes import ApiNode
from apification.utils import tpath
from apification.utils.xpath_reference import make_result, get_xpath_data


class A(ApiNode):
    class B1(ApiNode):
        class C(ApiNode):
            pass
    class B2(ApiNode):
        class C(ApiNode):
            class D(ApiNode):
                class A(ApiNode):
                    pass


# def subitem_in_collection(collection, subitem, restrict_to_start=True):
#     for row in collection:
#         if subitem in row and not (restrict_to_start and row[0] != subitem[0]):
#             return True
#     return False


def test_against_xpath():
    def func(node, expr):
        return tpath.parse(node, expr)
    tpath_data = make_result(A, func=func, exc=tpath.TPathError)
    xpath_data = get_xpath_data()

    diff = []

    for tpath_row, xpath_row in zip(tpath_data, xpath_data):
        if tpath_row[1] != xpath_row[1]:
            raise Exception(u'Invalid reference sort order: %s != %s' % (tpath_row[1], xpath_row[1]))
        if tpath_row[0] != xpath_row[0]:
            diff.append(('Valid distinction', tpath_row, xpath_row))
        elif tpath_row[0] and tpath_row[2] != xpath_row[2]:
            diff.append(('Result distinction', tpath_row, xpath_row))
    
    if diff:
        f_diff = u'\n'.join('\r' + '\t'.join(map(str, i)) for i in diff)
        raise AssertionError(u'Xpath and TPath diff: \n\n%s' % f_diff)
    