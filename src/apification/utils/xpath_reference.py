#!/usr/bin/env python

import itertools
from lxml import etree


class XPathReferrenceGenerator(object):
    LEXEMS = ('/', '//', '.', '..', '*', 'A', 'B1', 'C')
    LEXEMS_NUM = 4
    catched_exception = etree.XPathEvalError

    def __init__(self):
        self.data = []

    @classmethod
    def run(cls):
        obj = cls()
        node = obj.get_initial_node()
        obj.make_result(node)
        return obj

    def get_initial_node(self):
        root = self.get_tree()
        return root.find('B2')

    def get_tree(self):
        xml = """
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
        return etree.fromstring(xml)

    def eval_expr(self, node, expr):
        return node.xpath(expr)

    def exclude_expression(self, expr):
        return (
            expr.startswith('///')  # ambiguous expression - skip it
            or expr in ('.//.', '././/.', './/./.', './/.//.')  # lxml implementation seems to be different from spec
            or expr in ('/.//.', '/.//./.', '/././/.', '/.//.//.')  #  lxml seems to lose results here
        )

    def generate_expressions(self):
        for i in xrange(self.LEXEMS_NUM):
            for comb in itertools.combinations_with_replacement(self.LEXEMS, i+1):
                seen = []
                for item in itertools.permutations(comb):
                    expr = ''.join(item)
                    if not self.exclude_expression(expr) and expr not in seen:
                        seen.append(expr)
                        yield expr

    def make_result(self, node):
        for expr in self.generate_expressions():
            try:
                isvalid = True
                result = self.eval_expr(node, expr)
                if hasattr(result, '__iter__'):
                    result = map(self.get_name, result)
                else:
                    isvalid = False
                    result = u'NaN'
            except self.catched_exception as e:
                isvalid = False
                result = e.message
            self.data.append((isvalid, expr, result))

    def get_name(self, node):
        i = node
        full_name = [node.tag]
        
        while i.getparent() is not None:
            i = i.getparent()
            full_name.append(i.tag)

        return '.'.join(reversed(full_name))

    def print_result(self):
        for isvalid, expr, result in self.data:
            if isvalid:
                print 'OK:   \t%s \t %s' % (expr, result)
            else:
                print 'Fail: \t%s \t %s' % (expr, result)


class XPathClassTreeGenerator(XPathReferrenceGenerator):
    def get_class_tree(self):
        from apification.resources import Resource
        from apification import resource

        @resource
        class A(Resource):
            @resource
            class B1(Resource):
                @resource
                class C(Resource):
                    pass
            @resource
            class B2(Resource):
                @resource
                class C(Resource):
                    @resource
                    class D(Resource):
                        @resource
                        class A(Resource):
                            pass
        return A

    def get_tree(self):
        def create_nodes(node, xml_node):
            for name, subnode in node.children.iteritems():
                xml_subnode = etree.SubElement(xml_node, name)
                create_nodes(subnode, xml_subnode)

        root = self.get_class_tree()
        xml_root = etree.Element(root.__name__)
        create_nodes(root, xml_root)
        return xml_root
