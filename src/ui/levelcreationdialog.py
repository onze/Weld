
from PySide import QtGui,QtCore

class LevelCreationDialog(QtGui.QWidget):
    def __init__(self,parent,ext_oktrigger):
        QtGui.QWidget.__init__(self,parent,QtCore.Qt.Window)
        #external trigger
        self.ext_oktrigger=ext_oktrigger
        self.setup_ui()
        self.props={}

    def setup_ui(self):
        vl=QtGui.QVBoxLayout(self)

        w=QtGui.QWidget()
        vl.addWidget(w)
        hl=QtGui.QHBoxLayout(w)
        w.setLayout(hl)
        lbl=QtGui.QLabel('level name:')
        self.level_name=le=QtGui.QLineEdit(self)
        le.setText('MyLevel')
        [hl.addWidget(w) for w in [lbl,le]]

        w=QtGui.QWidget()
        vl.addWidget(w)
        hl=QtGui.QHBoxLayout(w)

        cancelbtn=QtGui.QPushButton('cancel',self)
        self.connect(cancelbtn,QtCore.SIGNAL('clicked()'),self.cancel_trigger)

        okbtn=QtGui.QPushButton('ok',self)
        self.connect(okbtn,QtCore.SIGNAL('clicked()'),self.ok_trigger)
        
        [hl.addWidget(w) for w in [cancelbtn,okbtn]]

    def ok_trigger(self):
        """
        Internal ok trigger.
        """
        self.props['__cancelled']=False
        self.props['name']=self.level_name.text()
        #TODO: check fields validity
        self.ext_oktrigger()

    def cancel_trigger(self):
        self.props['__cancelled']=True
        self.oktrigger()
