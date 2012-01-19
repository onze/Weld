
import sys

def curr_f():
    """
    returns info about the current function
    """
    frame = sys._getframe(1)
    filename = frame.f_code.co_filename
    lineno = frame.f_code.co_firstlineno
#    name='.'.join(frame.f_code.co_names)+'()'
    return filename + ' @ ' + str(lineno)#+': '+name

def pretty_print_dict(d, add_metadata=True):
    s = []
    if add_metadata:
        s.append('<dict of len %i>' % len(d))
    s.append('{')
    s.extend(['\t%s: %s,' % (k, pp(v, add_metadata)) for k, v in d.iteritems()])
    s.append('}')
    return '\n'.join(s)

def pp(o, add_metadata=True):
    """
    pretty print data structs.
    :param add_metadata: returned string may contain additional info about the
    given object, is possible.
    :type add_metadata: bool
    """
    dispatch = {dict:pretty_print_dict}
    if type(o) in dispatch:
        return dispatch[type(o)](o, add_metadata)
    else:
        return o.__repr__()

if __name__ == '__main__':
    d = dict(a=1, b=2, z=26)
    print pp(d)
