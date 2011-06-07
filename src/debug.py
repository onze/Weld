
import sys

def curr_f():
    """
    returns info about the current function
    """
    frame=sys._getframe(1)
    filename = frame.f_code.co_filename
    lineno=frame.f_code.co_firstlineno
    name='.'.join(frame.f_code.co_names)+'()'
    return filename+' @ '+str(lineno)+': '+name


