

__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

import sys

from PySide import QtGui
from PySide.QtCore import Qt

from QSteelWidget.PyQSteelWidget import QSteelWidget

class Ui(QtGui.QMainWindow):
    def __init__(self, weld):
        self.app = QtGui.QApplication(sys.argv)
        QtGui.QMainWindow.__init__(self, None)
        self.weld=weld
        
        self.setWindowTitle("Weld editor")
        self.resize(800, 600)
        self.show_status('loading internals...')

        #setup layout and main widgets
        self.setup_menu()
        self.setup_resources_browser()
        self.setup_central_widget()
        self.setup_property_browser()

    def show(self):
        QtGui.QMainWindow.show(self)
        return self.app.exec_()

    def setup_property_browser(self):
        #setup dock
        dockWidget = QtGui.QDockWidget('properties', self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dockWidget)
        #container widget
        self.props_browser={'widget':QtGui.QWidget()}
        hlayout = QtGui.QVBoxLayout()
        self.props_browser['widget'].setLayout(hlayout)
        dockWidget.setWidget(self.props_browser['widget'])


    def setup_central_widget(self):
        self.central_widget={'widget':QtGui.QTabWidget()}
        self.setCentralWidget(self.central_widget['widget'])

    def setup_resources_browser(self):
        #setup dock
        dockWidget = QtGui.QDockWidget('resources', self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea|Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockWidget)
        #container widget
        self.res_browser = {'widget':QtGui.QTabWidget()}
        dockWidget.setWidget(self.res_browser['widget'])

        #weld resources browser
        self.res_browser['weld_resources'] = QtGui.QToolBox()
        self.res_browser['widget'].addTab(self.res_browser['weld_resources'], 'weld resources')

        #level resources browser
        tree =self.res_browser['level_resources']= QtGui.QTreeView()

        model=QtGui.QDirModel()
        tree.setModel(model)

        self.res_browser['widget'].addTab(self.res_browser['level_resources'], 'level resources')

    def show_status(self, s, timeout=0):
        self.statusBar().showMessage(s, timeout)

    def setup_menu(self):
        self.menubar = {'widget':self.menuBar()}

        ################
        #file menu
        self.menubar['file'] = self.menubar['widget'].addMenu('File')

        #new level item
        self.menubar['file_newLevel'] = QtGui.QAction('new level', #title
                                                      self, #parent
                                                      shortcut=QtGui.QKeySequence.New,
                                                      statusTip='',
                                                      triggered=self.new_level_trigger)
        self.menubar['file'].addAction(self.menubar['file_newLevel'])

        #open level item
        self.menubar['file_openLevel'] = QtGui.QAction('open level', #title
                                                       self, #parent
                                                       shortcut=QtGui.QKeySequence.Open,
                                                       statusTip='',
                                                       triggered=self.open_level_trigger)
        self.menubar['file'].addAction(self.menubar['file_openLevel'])

        #save level item
        self.menubar['file_saveLevel'] = QtGui.QAction('save level', #title
                                                       self, #parent
                                                       shortcut=QtGui.QKeySequence.Save,
                                                       statusTip='',
                                                       triggered=self.save_level_trigger)
        self.menubar['file'].addAction(self.menubar['file_saveLevel'])

        #close level item
        self.menubar['file_closeLevel'] = QtGui.QAction('close level', #title
                                                        self, #parent
                                                        shortcut=QtGui.QKeySequence.Close,
                                                        statusTip='',
                                                        triggered=self.close_level_trigger)
        self.menubar['file'].addAction(self.menubar['file_closeLevel'])

        #quit
        self.menubar['file_quit'] = QtGui.QAction('quit', #title
                                                  self, #parent
                                                  shortcut='Ctrl+Q',
                                                  statusTip='',
                                                  triggered=self.quit_trigger)
        self.menubar['file'].addAction(self.menubar['file_quit'])

        ################
        #edit menu
        self.menubar['edit'] = self.menubar['widget'].addMenu('Edit')

        #undo last command
        self.menubar['edit_undo'] = QtGui.QAction('undo', #title
                                                  self, #parent
                                                  shortcut=QtGui.QKeySequence.Undo,
                                                  statusTip='',
                                                  triggered=self.undo_trigger)
        self.menubar['edit'].addAction(self.menubar['edit_undo'])

        #undo last undo
        self.menubar['edit_redo'] = QtGui.QAction('redo', #title
                                                  self, #parent
                                                  shortcut=QtGui.QKeySequence.Redo,
                                                  statusTip='',
                                                  triggered=self.redo_trigger)
        self.menubar['edit'].addAction(self.menubar['edit_redo'])

    def new_level_trigger(self):
        print 'Weld.new_level_trigger()'
        self.weld.new_level()

    def open_level_trigger(self):
        print 'Weld.open_level_trigger()'

    def save_level_trigger(self):
        print 'Weld.save_level_trigger()'

    def close_level_trigger(self):
        print 'Weld.close_level_trigger()'

    def quit_trigger(self):
        print 'Weld.quit_trigger()'
        self.close()

    def undo_trigger(self):
        print 'Weld.undo_trigger()'

    def redo_trigger(self):
        print 'Weld.redo_trigger()'

    def feed_resources(self,resources):
        """
        feeds the resources browser with a level resources
        """
        pass

    def add_engine_view(self,name):
        """
        instanciate a c++ QtOgreWidget and returns a pointer to it.
        """
        self.central_widget['qt_ogre_widget']=QSteelWidget()
        self.central_widget['widget'].addTab(self.central_widget['qt_ogre_widget'], name)






