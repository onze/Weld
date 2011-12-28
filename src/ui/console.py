
import sys

from PySide import QtGui

class Console(QtGui.QPlainTextEdit):
    instance = None
    def __init__(self, parent=None):
        QtGui.QPlainTextEdit.__init__(self, parent)
        Console.instance = self
        sys.stdout = Writer(self,
                            preHtml='<span style="color:black">',
                            postHtml='</span>',
                            dispatch_list=[sys.__stdout__]
                            )
        sys.stderr = Writer(self,
                            pre='\033[1;31m',
                            post='\033[1;m',
                            preHtml='<span style="color:red">',
                            postHtml='</span>',
                            dispatch_list=[sys.__stderr__]
                            )
        sys.warning = Writer(self,
                             pre='\033[1;33m',
                             post='\033[1;m',
                             preHtml='<span style="color:orange">',
                             postHtml='</span>',
                             dispatch_list=[sys.__stderr__]
                             )
        print 'console ready'

    def _write(self, s, pre, post):
        s = pre + self.toHtml(s) + post
        self.textCursor().insertHtml(s + '<br>')
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum()-3)

    def toHtml(self, s):
        """
        Transform the given string into its html equivalent.
        """
        for k, v in [
            ('>', '&gt;'),
            ('<', '&lt;'),
            ('\n', '<br>'),
            ('\t', '&nbsp;&nbsp;&nbsp;&nbsp;'),
            (' ', '&nbsp;'),
            ('\033[1;33m', '<span style="color:orange">'),
            ('\033[1;31m', '<span style="color:red">'),
            ('\033[1;m', '</span>'),
            ]:
            s = s.replace(k, v)
        return s

    @staticmethod
    def write(s, pre='', post=''):
        if not Console.instance:
            Console()
        Console.instance._write(s, pre, post)

class Writer:

    def __init__(self, console,
                 preHtml='', postHtml='',
                 pre='', post='',
                 dispatch_list=[]):
        self.console = console
        self.buffer = ''
        self.preHtml, self.postHtml = preHtml, postHtml
        self.pre, self.post = pre, post
        self.dispatch_list = dispatch_list

    def write(self, s):
        for fd in self.dispatch_list:
            print >> fd, self.pre + s + self.post,
        self.buffer += s
        if s == '\n' or s.endswith('\n'):
            self.console.write(self.buffer)
            self.buffer = ''

