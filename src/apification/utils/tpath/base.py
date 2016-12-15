import re


class TPathError(Exception):
    pass


class BaseLexemMetaclass(type):
    def __init__(cls, *args, **kwargs):
        super(BaseLexemMetaclass, cls).__init__(*args, **kwargs)
        if cls.pattern is not None:
            cls.pattern = re.compile(cls.pattern)


class BaseLexem(object):
    __metaclass__ = BaseLexemMetaclass
    pattern = None
    priority = 100

    def __init__(self, parser, node, token):
        self.node = node
        self.parser = parser
        self.proxy = self.parser.proxy
        self.token = token

    def __repr__(self):
        return u'<%s>' % self.pattern.pattern

    def resolve(self, iterator=None):
        raise NotImplementedError()


class TPathParserMetaclass(type):
    def __new__(cls, cls_name, cls_parents, cls_dict):
        from apification.utils.tpath.proxy import RootableProxyMixin

        if 'proxy' in cls_dict and cls_dict['proxy'] is not NotImplemented:
            cls_dict['proxy'] = RootableProxyMixin.make_rootable(cls_dict['proxy'])

        ret = super(TPathParserMetaclass, cls).__new__(cls, cls_name, cls_parents, cls_dict)
        return ret

    def __init__(cls, *args, **kwargs):
        super(TPathParserMetaclass, cls).__init__(*args, **kwargs)
        cls.separator_classes = getattr(cls, 'separator_classes', [])[:]
        cls.lexem_classes = getattr(cls, 'lexem_classes', [])[:]


class TPathParser(object):
    __metaclass__ = TPathParserMetaclass
    proxy = NotImplemented

    @classmethod
    def separator(cls, separator_class):
        if separator_class not in cls.separator_classes:
            cls.separator_classes.append(separator_class)
            cls.separator_classes.sort(key=lambda x: -x.priority)
        return separator_class

    @classmethod
    def lexem(cls, lexem_class):
        if lexem_class not in cls.lexem_classes:
            cls.lexem_classes.append(lexem_class)
            cls.lexem_classes.sort(key=lambda x: -x.priority)
        return lexem_class

    @classmethod
    def parse(cls, node, expression):
        parser = cls()

        expression_list = [expression]
        for lex_class in parser.lexem_classes:
            offset = 0
            for i, elem in enumerate(expression_list[:]):
                if isinstance(elem, basestring):
                    found = []
                    for m in re.finditer(lex_class.pattern, elem):
                        found.append((m, lex_class(parser, node, m.group(0))))
                    replacement = []
                    pos = 0
                    for m, lex in found:
                        replacement.append(elem[pos:m.start()])
                        replacement.append(lex)
                        pos = m.end()
                    replacement.append(elem[pos:])
                    replacement = filter(lambda x: x != '', replacement)

                    expression_list[i+offset:i+offset+1] = replacement
                    offset = len(replacement) - 1

        iterator = None
        for lex in expression_list:
            if isinstance(lex, basestring):
                raise TPathError(u'Unable to parse expression "%s"' % expression)
            iterator = lex.resolve(iterator)

        if iterator is None:
            return [node]
        else:
            return list(iterator)


__import__('apification.utils.tpath.lexems')
