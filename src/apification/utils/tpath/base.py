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


class BaseSeparator(BaseLexem):
    pass


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
        from apification.utils.tpath.proxy import VirtualRoot

        def is_match_only(pattern, text):
            match = (tuple(pattern.finditer(text)) or (None, ))[0]
            if match is None:
                return False
            return match.end() - match.start() == len(text)

        parser = cls()

        if not expression:
            raise TPathError(u'Empty expression')

        expression_list = []

        # splitting with separators
        separator_pattern = re.compile(u'|'.join(i.pattern.pattern for i in parser.separator_classes))
        pos = 0
        for m in separator_pattern.finditer(expression):
            if pos != m.start():  # non-empty string between separators
                expression_list.append(expression[pos:m.start()])
            elif expression_list:
                raise TPathError(u'Multiple separators in a row in "%s"' % expression)

            for sep in parser.separator_classes:
                if is_match_only(sep.pattern, m.group()):
                    expression_list.append(sep(parser, node, m.group()))
                    break
            else:
                raise AssertionError(u'Separator pattern not found in previously matched string')
            pos = m.end()

        if pos != len(expression):  # last string part
            expression_list.append(expression[pos:])
        elif expression != '/':  # special case
            assert expression_list and isinstance(expression_list[-1], BaseSeparator)
            raise TPathError(u'Trailing separators not allowed')

        # looking for internal lexems
        for i, expr in enumerate(expression_list[:]):
            if isinstance(expr, BaseSeparator):
                continue

            for lex in parser.lexem_classes:
                if is_match_only(lex.pattern, expr):
                    expression_list[i] = lex(parser, node, expr)
                    break
            else:
                raise TPathError(u'Unable to parse "%s" part of "%s" expression' % (expr, expression))

        iterator = None
        for lex in expression_list:
            if isinstance(lex, basestring):
                raise TPathError(u'Unable to parse expression "%s"' % expression)
            iterator = lex.resolve(iterator)

        if iterator is None:
            return [node]
        else:
            result = []
            for i in iterator:
                if i is not VirtualRoot and i not in result:
                    result.append(i)
            return result


__import__('apification.utils.tpath.lexems')
