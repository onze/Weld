
import sys
from itertools import izip

import ui
from PySide import QtGui
from debug import curr_f

class PropertyBrowser(QtGui.QTabWidget):
    def __init__(self):
        QtGui.QTabWidget.__init__(self)
        vlayout = QtGui.QVBoxLayout()
        self.setLayout(vlayout)
        self.tabs = []

    def on_steel_ready(self, qsteelwidget):
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
                def per_qte_on_change():
                    self.qte_changed(qte, model_type, model_id)
                json = qsw.ogreModelToJson(long(model_id))
                qte.setPlainText(json)
                qte.textChanged.connect(per_qte_on_change)
                #TODO: disconnect the qte at some point
                tab.addItem(qte, '%(model_type)s (id=%(model_id)s)' % locals())
            self.addTab(tab, str(id))

    def on_agents_deselected(self):
        print 'PropertyBrowser.on_agents_deselected()'
        self.clear()

    def qte_changed(self, qte, model_type, model_id):
        """
        Called when the text in a QPlainTextEdit is modified.
        (linkage is done in self.on_agents_selected)
        """
        print 'qte_changed', qte, model_type, model_id
        # check new json is still valid
        s = qte.document().toPlainText()
        try:
            eval(s)
        except Exception, e:
            print >> sys.stderr, curr_f(), ':\n', s, \
                '\nProperties description is not valid json:\n', e.args
            return
        qsw = ui.Ui.instance().qsteelwidget
        r = qsw.ogreModelFromJson(long(model_id), s)
        if not r:
            print >> sys.stderr, 'model rejected change (see log).'

