
import sys

def curr_f():
    """
    returns info about the current function
    """
    frame=sys._getframe(1)
    filename = frame.f_code.co_filename
    lineno=frame.f_code.co_firstlineno
#    name='.'.join(frame.f_code.co_names)+'()'
    return filename+' @ '+str(lineno)#+': '+name

def pretty_print_dict(d):
    s=['<dict of len %i>{'%len(d)]
    s.extend(['\t%s: %s,'%i for i in d.items()])
    s.append('}')
    return '\n'.join(s)

def pp(o):
    """
    pretty print data structs.
    """
    dispatch={dict:pretty_print_dict}
    if type(o) in dispatch:
        return dispatch[type(o)](o)
    else:
        return o.__repr__()




if __name__=='__main__':
    d=dict(a=1,b=2,z=26)
    print pp(d)
