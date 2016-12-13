#!/usr/bin/python

from lxml import etree

def main():
    xml ="""
    <A>
        <B1>
            <C>
            </C>
        </B1>
        <B2>
            <C>
                <D>
                    <A>
                    </A>
                </D>
            </C>
        </B2>
    </A>
    """
    while ' ' in xml:
        xml = xml.replace(' ','')
    xml = xml.replace('\n','')
    
    
    root = etree.fromstring(xml)
    
    root_A = root
    B1, B2 =  root_A.getchildren()
    B1_C = B1.getchildren()[0]
    B2_C = B2.getchildren()[0]
    D = B2_C.getchildren()[0]
    inner_A = D.getchildren()[0]
    
    
    #   / // .  .. * nodename
    #
    
    
    lexems = ['/', '//', '.', '..', '*', 'A', 'B1', 'C']
    
    import itertools
    
    
    def comb(num=2):
        for item in itertools.permutations(lexems, num):
            yield ''.join(item)
        
    
    
    def do(node):
        results = []
        for expr in comb(3):
            try:
                results.append((expr, True, node.xpath(expr)))
            except etree.XPathEvalError as e:
                results.append((expr, False, e.message))
        return results
    
    
    def get_full_name(node):
        i = node
        full_name = [node.tag]
        
        while i.getparent():
            i = i.getparent()
            full_name.append(i.tag)
        
        return '.'.join(reversed(full_name))
    
    def print_result(data):
        for expr, isvalid, result in data:
            if isvalid:
                names = []
                if hasattr(result, '__iter__'):
                    for i in result:
                        names.append(get_full_name(i))
                else:
                    names = result
                print 'OK: %s \t Expression: %s \t Nodes: %s' % (isvalid, expr, names)
            else:
                print 'OK: %s \t Expression: %s \t Nodes: %s' % (isvalid, expr, result)
            
    print_result(do(root_A))
    
if __name__ == '__main__':
    main()


    
    
    
    