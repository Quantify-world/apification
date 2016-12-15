from apification.nodes import ApiNode
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


def test_against_xpath():
    def func(node, expr):
        return tpath.parse(node, expr)
    tpath_data = TPathGenerator.run().data
    xpath_data = XPathClassTreeGenerator.run().data

    diff = []
    match = []

    for tpath_row, xpath_row in zip(tpath_data, xpath_data):
        if tpath_row[1] != xpath_row[1]:
            raise Exception(u'Invalid reference sort order: %s != %s' % (tpath_row[1], xpath_row[1]))
        if tpath_row[0] != xpath_row[0]:
            diff.append(('Valid distinction', tpath_row, xpath_row))
        elif tpath_row[0] and tpath_row[2] != xpath_row[2]:
            diff.append(('Result distinction', tpath_row, xpath_row))
        else:
            match.append(tpath_row)

    print u'Matches:\n' + u'\n'.join(map(str, match))

    print '%s matches / %s total' % (len(match), len(xpath_data))
    if diff:
        f_diff = u'\n\r \n'.join(u'\r%s\ttpath: %s\n\r%s\txpath: %s' % (msg, tp, ' '*(1+len(msg)), xp) for msg, tp, xp in diff)
        # f_diff = u'\n'.join('\r' + '\t'.join(map(str, i)) for i in diff)
        raise AssertionError(u'Xpath and TPath diff: \n\n%s' % f_diff)
