import xmltodict

def normalise_dict(d):
    """
    Recursively convert dict-like object (eg OrderedDict) into plain dict.
    Sorts list values.
    """
    out = {}
    for k, v in dict(d).items():
        if hasattr(v, 'items'):
            out[k] = normalise_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in sorted(v, key=lambda x: sorted(x.keys())):
                if hasattr(item, 'items'):
                    out[k].append(normalise_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def xml_compare(a, b):
    a = normalise_dict(xmltodict.parse(a))
    b = normalise_dict(xmltodict.parse(b))
    return a == b

