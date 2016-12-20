from apification.utils import tpath
from apification.utils.xpath_reference import XPathClassTreeGenerator


class TPathGenerator(XPathClassTreeGenerator):
    catched_exception = tpath.TPathError

    def get_initial_node(self):
        root = self.get_tree()
        return root.B2

    def get_tree(self):
        return self.get_class_tree()

    def eval_expr(self, node, expr):
        return tpath.parse(node, expr)

    def get_name(self, node):
        return unicode(node)

def test_tpath():
    B2 = TPathGenerator().get_initial_node()
    A = B2.parent_class
    assert tpath.parse(B2, '..') == [A]


def test_against_xpath():
    def func(node, expr):
        return tpath.parse(node, expr)
    tpath_data = TPathGenerator.run().data
    xpath_data = XPathClassTreeGenerator.run().data

    v_diff = []
    r_diff = []
    match = []

    for tpath_row, xpath_row in zip(tpath_data, xpath_data):
        if tpath_row[1] != xpath_row[1]:
            raise Exception(u'Invalid reference sort order: %s != %s' % (tpath_row[1], xpath_row[1]))

        if tpath_row[0] != xpath_row[0]:
            v_diff.append(('Valid distinction', tpath_row, xpath_row))
        elif tpath_row[0] and sorted(tpath_row[2]) != sorted(xpath_row[2]):
            r_diff.append(('Result distinction', tpath_row, xpath_row))
        else:
            match.append(tpath_row)

    # print u'Matches:\n' + u'\n'.join(map(str, match))
    print '%s matches / %s total' % (len(match), len(xpath_data))

    if v_diff or r_diff:
        f_diff = u'\n\r \n'.join(u'\r%s\txpath: %s\n\r%s\ttpath: %s' % (msg, xp, ' '*(1+len(msg)), tp) for msg, tp, xp in v_diff)
        f_diff += u'\n\r \n\r \n\r ' + u'\n\r \n'.join(u'\r%s\txpath: %s\n\r%s\ttpath: %s' % (msg, xp, ' '*(1+len(msg)), tp) for msg, tp, xp in r_diff)
        # f_diff = u'\n'.join('\r' + '\t'.join(map(str, i)) for i in diff)
        raise AssertionError(u'Xpath and TPath diff: \n\n%s' % f_diff)
