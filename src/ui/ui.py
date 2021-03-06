import sys
from console import Console
from console import Writer

import os
from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import Qt
from config import Config
from levelcreationdialog import LevelCreationDialog
from propertybrowser import PropertyBrowser

try:
    from plugins import QSteelWidget
    #print 'dir(QSteelWidget):'
    #print '\t','\n\t'.join(sorted(dir(QSteelWidget)))
except Exception, e:
    print >> sys.__stderr__, 'Caught an exception while loading the qsteelwidget.\n' \
        'libPyQSteelWidget.so is expected to be located in <weld\'s root dir>/plugins,' \
        ' or its directory to be part of LD_LIBRARY_PATH.\n' \
        'This shared library contains the Steel engine binding widget. You can '\
        'download it from https://github.com/onze/QSteelWidget \n' \
        'Original error was:'
    raise


class Ui(QtGui.QMainWindow, object):
    """singleton"""
    __instance = None

    def __init__(self, weld):
        if Ui.__instance is None:
            Ui.__instance = self
        else:
            raise Exception('can declare new Ui instance. Ui is a singleton.')
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

    def BT_export_trigger(self):
        print 'Ui.BT_export_trigger()'
        self.weld.BT_export()

    def export_level_trigger(self):
        print 'Ui.export_level_trigger()'
        self.weld.export_level()

    def close_level_creation_dialog(self):
        """
        as in close the level-creation-dialog,
        not close-level-creation dialog, if that makes sense.
        """
        print 'Ui.close_level_creation_dialog()'
        idx = self.central_widget['widget'].indexOf(self.central_widget['level_creation_dialog'])
        self.central_widget['widget'].removeTab(idx)
        del self.central_widget['level_creation_dialog']

    def close_level_trigger(self):
        print 'Ui.close_level_trigger()'
        print 'Ui.close_level()'
        self.weld.close_level()

    def close_project_trigger(self):
        print 'Ui.close_project_trigger()'
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
        if name is not None and 'qsteelwidget' in self.central_widget:
            idx = self.central_widget['widget'].indexOf(self.central_widget['qsteelwidget'])
            self.central_widget['widget'].setTabText(idx, name)
        self.update_window_title()

    def new_level_trigger(self):
        self.weld.new_level()

    def new_project_trigger(self):
        self.weld.new_project()

    def on_steel_ready(self, qsteelwidget):
        self.props_browser['propsbrowser'].on_steel_ready(qsteelwidget)
        #qsteelwidget.onNewLogLine.connect(Console.write)

    def open_level_creation_dialog(self, oktrigger):
        if self.oktrigger is not None:
            raise Exception('oktrigger is not None: %s' % (str(self.oktrigger)))
        self.oktrigger = oktrigger
        self.central_widget['level_creation_dialog'] = form = LevelCreationDialog(self, self.level_creation_dialog_ok)
        idx = self.central_widget['widget'].addTab(form, 'new level dialog')
        self.central_widget['widget'].setTabEnabled(idx, True)
        return form

    def open_level_trigger(self):
        print 'UI.open_level_trigger()'

    def open_project_trigger(self):
        self.weld.open_project()

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
        instanciate a c++ QtSteelWidget and returns a pointer to it.
        this widget is responsible for calling steel methods.
        """
        if 'qsteelwidget' not in self.central_widget:
            self.central_widget['qsteelwidget'] = qsteelwidget = QSteelWidget()
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
        self.props_browser = {'propsbrowser':PropertyBrowser()}
        dockWidget.setWidget(self.props_browser['propsbrowser'])

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
        self.res_browser['library'] = tree
        self.res_browser['widget'].addTab(self.res_browser['library'], 'library')

        #level browser
        tree = QtGui.QTreeView()
        model = QtGui.QFileSystemModel()
        tree.setModel(model)
        self.res_browser['level'] = tree
        self.res_browser['widget'].addTab(tree, 'level')

    def set_resources_draggable(self, draggable):
        self.res_browser['library'].setDragEnabled(draggable)
        self.res_browser['level'].setDragEnabled(draggable)

    def show(self):
        QtGui.QMainWindow.show(self)
        if 'qsteelwidget' in self.central_widget and not Config.instance().show_ogre_init:
            self.qsteelwidget.onNewLogLine.connect(Console.write)
        return self.app.exec_()

    def show_status(self, s, timeout=0):
        self.statusBar().showMessage(s, timeout)

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
        #project menu
        self.menubar['project'] = self.menubar['widget'].addMenu('Project')

        #new project item
        self.menubar['project_newProject'] = QtGui.QAction('new', #title
                                                           self, #parent
                                                           shortcut='Ctrl+Shift+N',
                                                           statusTip='',
                                                           triggered=self.new_project_trigger)
        self.menubar['project'].addAction(self.menubar['project_newProject'])

        #open project item
        self.menubar['project_openProject'] = QtGui.QAction('open', #title
                                                            self, #parent
                                                            shortcut='Ctrl+Shift+O',
                                                            statusTip='',
                                                            triggered=self.open_project_trigger)
        self.menubar['project'].addAction(self.menubar['project_openProject'])

        #save project item
        self.menubar['project_saveProject'] = QtGui.QAction('save', #title
                                                            self, #parent
                                                            shortcut='Ctrl+Shift+S',
                                                            statusTip='',
                                                            triggered=self.save_project_trigger)
        self.menubar['project'].addAction(self.menubar['project_saveProject'])

        #close project item
        self.menubar['project_closeProject'] = QtGui.QAction('close', #title
                                                             self, #parent
                                                             shortcut='Ctrl+Shift+W',
                                                             statusTip='',
                                                             triggered=self.close_project_trigger)
        self.menubar['project'].addAction(self.menubar['project_closeProject'])

        self.menubar['project'].addSeparator()

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

        ################
        #behavor trees menu
        self.menubar['BT'] = self.menubar['widget'].addMenu('Behavior Trees')
        #quit
        self.menubar['BT_export'] = QtGui.QAction('export to Steel', #title
                                                  self, #parent
                                                  shortcut='Ctrl+B',
                                                  statusTip='',
                                                  triggered=self.BT_export_trigger)
        self.menubar['BT'].addAction(self.menubar['BT_export'])









