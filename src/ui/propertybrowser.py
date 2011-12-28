from itertools import izip

import ui
from PySide import QtGui

class PropertyBrowser(QtGui.QTabWidget):
    def __init__(self):
        QtGui.QTabWidget.__init__(self)
        vlayout = QtGui.QVBoxLayout()
        self.setLayout(vlayout)
        self.tabs = []

    def on_steel_ready(self):
        qsteelwidget = ui.Ui.instance().qsteelwidget
        qsteelwidget.onAgentsSelected.connect(self.on_agents_selected)
        qsteelwidget.onAgentsDeselected.connect(self.on_agents_deselected)

    def on_agents_selected(self, ids):
        """
        Will display properties for each selected agent id.
        """
        print 'PropertyBrowser.on_agents_selected():', ids
        qsw = ui.Ui.instance().qsteelwidget
        jsons = qsw.getAgentsJsons(ids)
        for id, json in izip(ids, jsons):
            tab = QtGui.QToolBox()
            try:
                d = eval(json)
            except Exception, e:
                print >> sys.stderr, 'in PropertyBrowser.on_agents_selected(),'\
                    ' for agent id=%s, cannot eval json:\n%s\nSkipping model. '\
                    'Original error was: %s' % map(str, [id, json, e.args])
            # display the agent's models props in separate qtextedit's
            # laid out in a column (qtoolbox)
            for model_type, model_id in d.iteritems():
                qte = QtGui.QPlainTextEdit()
                json = qsw.ogreModelJson(long(model_id))
                qte.setPlainText(json)
                tab.addItem(qte, '%(model_type)s (id=%(model_id)s)' % locals())
            self.addTab(tab, str(id))

    def on_agents_deselected(self):
        print 'PropertyBrowser.on_agents_deselected()'
        self.clear()
