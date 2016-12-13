#!/usr/bin/env python

import itertools
from lxml import etree

LEXEMS = ('/', '//', '.', '..', '*', 'A', 'B1', 'C')
LEXEMS_NUM = 3
XML_TREE = """
<A>
    <B1>
        <C />
    </B1>
    <B2>
        <C>
            <D>
                <A />
            </D>
        </C>
    </B2>
</A>
""".replace(' ','').replace('\n','')


def generate_expressions(num=LEXEMS_NUM):
    for item in itertools.permutations(LEXEMS, num):
        yield ''.join(item)


def make_result(node, func, exc):
    data = []
    for expr in generate_expressions():
        try:
            isvalid = True
            result = func(node, expr)
            if not hasattr(result, '__iter__'):
                isvalid = False
                result = u'NaN'
        except exc as e:
            isvalid = False
            result = e.message
        data.append((isvalid, expr, result))
    return data


def get_full_name(node):
    i = node
    full_name = [node.tag]
    
    while i.getparent():
        i = i.getparent()
        full_name.append(i.tag)
    
    return '.'.join(reversed(full_name))


def get_xpath_data():
    root = etree.fromstring(XML_TREE)
    
    root_A = root
    # B1, B2 =  root_A.getchildren()
    # B1_C = B1.getchildren()[0]
    # B2_C = B2.getchildren()[0]
    # D = B2_C.getchildren()[0]
    # inner_A = D.getchildren()[0]

    def func(node, expr):
        return node.xpath(expr)

    return make_result(root_A, func=func, exc=etree.XPathEvalError)


def print_result(data):
    for isvalid, expr, result in data:
        if isvalid:
            names = []
            for i in result:
                names.append(get_full_name(i))
            print 'OK:   \t%s \t %s' % (expr, names)
        else:
            print 'Fail: \t%s \t %s' % (expr, result)


def main():
    data = get_xpath_data()
    print_result(data)
    
if __name__ == '__main__':
    main()
