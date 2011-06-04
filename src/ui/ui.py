
import os.path


__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

import sys

import os
from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import Qt

from config import Config
from console import Console, Writer
from levelcreationdialog import LevelCreationDialog

#libPyQSteelWidget.so is expected to be located in the current directory.
#This shared library contains the Steel engine binding widget. You can compile
#it with the QSteelWidget project @ 
QSteelWidget = __import__('PyQSteelWidget').QSteelWidget

class Ui(QtGui.QMainWindow):
    """singleton"""
    __instance = None

    def __init__(self, weld):
        Ui.__instance = self
        self.app = QtGui.QApplication(sys.argv)
        QtGui.QMainWindow.__init__(self, None)
        self.weld = weld

        #used for window title
        self._project_name = None
        self._level_name = None
        
        self.update_window_title()
        self.resize(800, 600)
        self.show_status('loading internals...')

        #setup main widgets
        self.setup_menu()
        self.setup_resources_browser()
        self.setup_console()
        self.setup_property_browser()
        self.setup_central_widget()

    def close_level_creation_dialog(self):
        idx = self.central_widget['widget'].indexOf(self.central_widget['level_creation_dialog'])
        self.central_widget['widget'].removeTab(idx)
        del self.central_widget['level_creation_dialog']

    def close_level_trigger(self):
        self.weld.close_level()

    def close_project_trigger(self):
        self.weld.close_project()

    @staticmethod
    def instance():
        if Ui.__instance is None:
            raise Exception('no ui created.')
        return Ui.__instance

    def level_creation_dialog_ok(self):
        form = self.central_widget['level_creation_dialog']
        props = dict(form.props)
        if None in props.values():
            print 'props:', props
            self.show_status('all level properties should be filled !')
            return
        self.close_level_creation_dialog()
        if not props['__cancelled']:
            self.oktrigger(props)

    @property
    def level_name(self):
        return self._level_name

    @level_name.setter
    def level_name(self, name):
        self._level_name = name
        self.update_window_title()

    def new_level_trigger(self):
        self.weld.new_level()

    def new_project_trigger(self):
        self.weld.new_project()

    def open_level_creation_dialog(self, oktrigger):
        if self.oktrigger is not None:
            raise Exception('oktrigger is not None: %s' % (str(self.oktrigger)))
        self.oktrigger = oktrigger
        self.central_widget['level_creation_dialog'] = form = LevelCreationDialog(self, self.level_creation_dialog_ok)
        idx = self.central_widget['widget'].addTab(form, 'new level dialog')
        self.central_widget['widget'].setTabEnabled(idx, True)
        return form

    @property
    def project_name(self):
        return self._project_name

    @project_name.setter
    def project_name(self, name):
        self._project_name = name
        self.update_window_title()

    @property
    def qsteelwidget(self):
        """
        instanciate a c++ QtOgreWidget and returns a pointer to it.
        """
        if 'qsteelwidget' not in self.central_widget:
            self.central_widget['qsteelwidget'] = qsteelwidget = QSteelWidget()
            writer = Writer(Console.instance,
                            pre='<span style="color:green">',
                            post='</span>',
                            dispatch_list=[sys.__stdout__])
            if Config.instance().show_ogre_init:
                qsteelwidget.onNewLogLine.connect(Console.write)
            self.central_widget['widget'].addTab(qsteelwidget, 'Steel view')
        return self.central_widget['qsteelwidget']

    def quit_trigger(self):
        self.show_status('quitting...')
        self.close()

    def redo_trigger(self):
        print 'UI.redo_trigger()'

    def save_level_trigger(self):
        self.weld.save_level()

    def save_project_trigger(self):
        self.weld.save_project()

    def select_directory(self, basedir):
        dialog = QtGui.QFileDialog(None)
        dialog.setDirectory(basedir)
        dialog.setFileMode(QtGui.QFileDialog.Directory)
        dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, True)
        dialog.exec_()
        return dialog.selectedFiles()[0]

    def select_file(self, startdir=None, extensions=None, label='Select a file'):
        """
        Opens up a dialog to select a file. returns its path, or none if the
        dialog is aborted.
        """
        if startdir is None:
            startdir = os.getcwd()
        if extensions is None:
            extensions = ["All Files (*)"]
        elif not isinstance(extensions, list):
            extensions = [extensions]
        filename, _ = QtGui.QFileDialog.getOpenFileName(self,
                                                        label,
                                                        startdir,
                                                        ';;'.join(extensions))
        if not os.path.exists(filename):
            return None
        return filename

    def set_resources(self, model):
        """
        populates the resources browser with the given model. Resources are
        contained in a filesystem structure, so a treeview is used.
        """
        tree = self.res_browser['resources']
        tree.setModel(model)
        tree.setRootIndex(model.index(model.rootPath()));

        #make it look a bit more like a resources browser
        tree.hideColumn(2)
        tree.hideColumn(3)
        tree.sortByColumn(0, Qt.AscendingOrder)
        #expand main categories
        dir = model.rootDirectory()
        dir.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        for entry in dir.entryInfoList():
            index = model.index(model.rootDirectory().path() + '/' + entry.fileName())
            tree.setExpanded(index, True)
        tree.setRootIsDecorated(False)
        tree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def setup_central_widget(self):
        self.central_widget = {'widget':QtGui.QTabWidget()}
        self.oktrigger = None
        self.setCentralWidget(self.central_widget['widget'])

    def setup_console(self):
        #setup dock
        dockWidget = QtGui.QDockWidget('console', self)
        dockWidget.setAllowedAreas(Qt.BottomDockWidgetArea)
        self.addDockWidget(Qt.BottomDockWidgetArea, dockWidget)
        
        #setup console in it
        console = Console()
        console.setFixedHeight(100)
        dockWidget.setWidget(console)
        self.console = console

    def setup_property_browser(self):
        #setup dock
        dockWidget = QtGui.QDockWidget('properties', self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dockWidget)
        #container widget
        self.props_browser = {'widget':QtGui.QWidget()}

        vlayout = QtGui.QVBoxLayout()
        self.props_browser['widget'].setLayout(vlayout)
        vlayout.addWidget(QtGui.QPushButton('test button'))
        dockWidget.setWidget(self.props_browser['widget'])

    def setup_resources_browser(self):
        """
        filled with set_resources().
        """
        #setup dock
        dockWidget = QtGui.QDockWidget('resources', self)
        dockWidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dockWidget)
        #container widget
        self.res_browser = {'widget':QtGui.QTabWidget()}
        dockWidget.setWidget(self.res_browser['widget'])

        #weld resources browser
        tree = QtGui.QTreeView()
        tree.setDragEnabled(True)
        self.res_browser['resources'] = tree
        self.res_browser['widget'].addTab(self.res_browser['resources'], 'library')

        #level browser
        tree = QtGui.QTreeView()
        model = QtGui.QFileSystemModel()
        tree.setModel(model)
        self.res_browser['level'] = tree
        self.res_browser['widget'].addTab(tree, 'level')

    def show(self):
        QtGui.QMainWindow.show(self)
        if not Config.instance().show_ogre_init:
            self.qsteelwidget.onNewLogLine.connect(Console.write)
        return self.app.exec_()

    def show_status(self, s, timeout=0):
        self.statusBar().showMessage(s, timeout)

    def open_project_trigger(self):
        self.weld.open_project()

    def open_level_trigger(self):
        print 'UI.open_level_trigger()'

    def undo_trigger(self):
        print 'UI.undo_trigger()'

    def update_window_title(self):
        title = 'Weld editor'
        if self._project_name:
            title += ' -- ' + self._project_name
        if self._level_name:
            title += ' - ' + self._level_name
        self.setWindowTitle(title)

    def setup_menu(self):
        self.menubar = {'widget':self.menuBar()}

        ################
        #file menu
        self.menubar['file'] = self.menubar['widget'].addMenu('File')

        #new project item
        self.menubar['file_newProject'] = QtGui.QAction('new project', #title
                                                        self, #parent
                                                        shortcut='Ctrl+Shift+N',
                                                        statusTip='',
                                                        triggered=self.new_project_trigger)
        self.menubar['file'].addAction(self.menubar['file_newProject'])

        #open project item
        self.menubar['file_openProject'] = QtGui.QAction('open project', #title
                                                         self, #parent
                                                         shortcut='Ctrl+Shift+O',
                                                         statusTip='',
                                                         triggered=self.open_project_trigger)
        self.menubar['file'].addAction(self.menubar['file_openProject'])

        #save project item
        self.menubar['file_saveProject'] = QtGui.QAction('save project', #title
                                                         self, #parent
                                                         shortcut='Ctrl+Shift+S',
                                                         statusTip='',
                                                         triggered=self.save_project_trigger)
        self.menubar['file'].addAction(self.menubar['file_saveProject'])

        #close project item
        self.menubar['file_closeProject'] = QtGui.QAction('close project', #title
                                                          self, #parent
                                                          shortcut='Ctrl+Shift+W',
                                                          statusTip='',
                                                          triggered=self.close_project_trigger)
        self.menubar['file'].addAction(self.menubar['file_closeProject'])

        self.menubar['file'].addSeparator()

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



        ################
        #level menu
        self.menubar['level'] = self.menubar['widget'].addMenu('Level')
        #new level item
        self.menubar['level_new'] = QtGui.QAction('new', #title
                                                  self, #parent
                                                  shortcut=QtGui.QKeySequence.New,
                                                  statusTip='',
                                                  triggered=self.new_level_trigger)
        self.menubar['level'].addAction(self.menubar['level_new'])

        #open level item
        self.menubar['level_open'] = QtGui.QAction('open', #title
                                                   self, #parent
                                                   shortcut=QtGui.QKeySequence.Open,
                                                   statusTip='',
                                                   triggered=self.open_level_trigger)
        self.menubar['level'].addAction(self.menubar['level_open'])

        #save level item
        self.menubar['level_save'] = QtGui.QAction('save', #title
                                                   self, #parent
                                                   shortcut=QtGui.QKeySequence.Save,
                                                   statusTip='',
                                                   triggered=self.save_level_trigger)
        self.menubar['level'].addAction(self.menubar['level_save'])

        #close level item
        self.menubar['level_close'] = QtGui.QAction('close', #title
                                                    self, #parent
                                                    shortcut=QtGui.QKeySequence.Close,
                                                    statusTip='',
                                                    triggered=self.close_level_trigger)
        self.menubar['level'].addAction(self.menubar['level_close'])









