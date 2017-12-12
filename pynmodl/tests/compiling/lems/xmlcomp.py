import xmltodict


def xml_compare(a, b):
    a = setify_dict(xmltodict.parse(a))
    b = setify_dict(xmltodict.parse(b))
    return a == b


class hashabledict(dict):
    def __key(self):
        return tuple((k, self[k]) for k in sorted(self))

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return self.__key() == other.__key()


def setify_dict(d):
    out = {}
    for k, v in hashabledict(d).items():
        if hasattr(v, 'items'):
            out[k] = setify_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in v:
                if hasattr(item, 'items'):
                    out[k].append(setify_dict(item))
                else:
                    out[k].append(item)
            out[k] = frozenset(out[k])
        else:
            out[k] = v
    return hashabledict(out)


def test_xml_compare():
    snip1 = '''
    <dyn>
        <var value="3" name="x"/>
        <var name="z" value="2"/>
        <var value="1" name="w"/>
    </dyn>
    '''

    snip2 = '''
    <dyn>
        <var name="z" value="2"/>
        <var name="x" value="3"/>
        <var value="1" name="w"/>
    </dyn>
    '''

    assert(xml_compare(snip1, snip2))
