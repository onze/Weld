
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
        #sys.stderr = Writer(self,
        #                    pre='<span style="color:red">',
        #                    post='</span>',
        #                    dispatch_list=[sys.__stderr__]
        #                    )
        sys.warning = Writer(self,
                             pre='<span style="color:orange">',
                             post='</span>',
                             dispatch_list=[sys.__stderr__]
                             )

    def _write(self, s):
        self.textCursor().insertHtml(s)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


    @staticmethod
    def write(s):
        if not Console.instance:
            Console()
        Console.instance._write(s)

class Writer:

    def __init__(self, console, pre='', post='', dispatch_list=[]):
        self.console = console
        self.buffer = ''
        self.pre = pre
        self.post = post
        self.dispatch_list = dispatch_list

    def toHtml(self,s):
        for k, v in [('>','&gt;'),
            ('<','&lt;'),
            ('\n','<br>'),
            ('\t','&nbsp;&nbsp;&nbsp;&nbsp;')
            ]:
            s = s.replace(k, v)
        return s

    def write(self, s):
        for fd in self.dispatch_list:
            print >> fd, s,
        self.buffer += self.toHtml(s)
        if s == '\n' or s.endswith('\n'):
            self.console.write(self.pre + self.buffer + self.post)
            self.buffer = ''

