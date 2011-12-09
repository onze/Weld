
import sys

from PySide import QtGui

class Console(QtGui.QPlainTextEdit):
    instance = None
    def __init__(self, parent=None):
        QtGui.QPlainTextEdit.__init__(self, parent)
        Console.instance = self
        sys.stdout = Writer(self,
                            pre='<span style="color:black">',
                            post='</span>',
                            dispatch_list=[sys.__stdout__]
                            )
        sys.stderr = Writer(self,
                            pre='<span style="color:red">',
                            post='</span>',
                            dispatch_list=[sys.__stderr__]
                            )
        sys.warning = Writer(self,
                             pre='<span style="color:orange">',
                             post='</span>',
                             dispatch_list=[sys.__stderr__]
                             )
        print 'console ready'

    def _write(self, s, pre, post):
        s=pre+self.toHtml(s)+post
        self.textCursor().insertHtml(s+'<br>')
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()-3)

    def toHtml(self,s):
        """
        Transform the given string into its html equivalent.
        """
        for k, v in [('>','&gt;'),
            ('<','&lt;'),
            ('\n','<br>'),
            ('\t','&nbsp;&nbsp;&nbsp;&nbsp;'),
            (' ','&nbsp;'),
            ]:
            s = s.replace(k, v)
        return s

    @staticmethod
    def write(s,pre='',post=''):
        if not Console.instance:
            Console()
        Console.instance._write(s,pre,post)

class Writer:

    def __init__(self, console, pre='', post='', dispatch_list=[]):
        self.console = console
        self.buffer = ''
        self.pre = pre
        self.post = post
        self.dispatch_list = dispatch_list

    def write(self, s):
        for fd in self.dispatch_list:
            print >> fd, s,
        self.buffer+=s
        if s == '\n' or s.endswith('\n'):
            self.console.write(self.buffer,pre=self.pre,post=self.post)
            self.buffer = ''

