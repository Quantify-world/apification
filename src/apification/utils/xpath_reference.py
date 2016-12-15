#!/usr/bin/env python

import itertools
from lxml import etree


class XPathReferrenceGenerator(object):
    LEXEMS = ('/', '//', '.', '..', '*', 'A', 'B1', 'C')
    LEXEMS_NUM = 3
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

    def generate_expressions(self):
        for item in itertools.permutations(self.LEXEMS, self.LEXEMS_NUM):
            yield ''.join(item)

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
        from apification.nodes import ApiNode

        class A(ApiNode):
            class B1(ApiNode):
                class C(ApiNode):
                    pass
            class B2(ApiNode):
                class C(ApiNode):
                    class D(ApiNode):
                        class A(ApiNode):
                            pass
        return A

    def get_tree(self):
        def create_nodes(node, xml_node):
            for subnode in node.iter_class_children():
                xml_subnode = etree.SubElement(xml_node, subnode.name)
                create_nodes(subnode, xml_subnode)

        root = self.get_class_tree()
        xml_root = etree.Element(root.__name__)
        create_nodes(root, xml_root)
        return xml_root


# def nested_classes_to_xml(cls, seen=None):
#     if not isclass(cls):
#         raise ValueError(u'class expected, but %s given' % type(cls))
#     if seen is None:
#         seen = []
#     name = cls.__name__
#     subxml = []
# 
#     for attr_name in dir(cls):
#         if not attr_name.startswith('__'):
#             attr_value = getattr(cls, attr_name)
#             if attr_value in seen:
#                 raise ValueError(u'nested classes with recoursive ierarchy can not be converted to XML (...%s.%s links to %s creating a loop)' % (cls, attr_name, attr_value))
#             if isclass(attr_value):
#                 subxml.append(nested_classes_to_xml(attr_value, seen=seen+[cls]))
# 
#     return '<%s/>' % name if not subxml else '<%s>%s</%s>' % (name, ''.join(subxml), name)
