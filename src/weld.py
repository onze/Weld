import os.path

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

from config import Config
import os
import sys
from PySide import QtCore, QtGui
from level import Level
from project import Project
from resourcemanager import ResourceManager
from ui.ui import Ui
from savable import Savable

class Weld(Savable):
    """
    Main class of the editor.
    """
    def __init__(self, parent=None):
        Savable.__init__(self, savepath=os.path.join(sys.path[0], 'weld.cache'))
        self.savelist += ['current_project_path']
        self.current_project_path = None

        Ui(self)

        #setup internal resource handlers
        self.project = None
        
        #list of resources we can ask steel to load
        self.resMan = ResourceManager(os.path.join(Config.instance().weld_data_path, 'resources'))
        self.resMan.attach_to_Ui(Ui.instance().res_browser['library'])

        #ready
        Ui.instance().show_status('ready', 1000)
        self.load()
        if Config.instance().on_open_reopen_last_project:
            if self.current_project_path is not None:
                print 'auto reopening project %s.' % self.current_project_path
                p, f = os.path.split(self.current_project_path)
                self.open_project(self.current_project_path, f)
            else:
                print 'no project to reopen.'
        else:
            print 'skipping project reopening.'

    def close_project(self):
        Ui.instance().set_resources_draggable(False)
        raise NotImplementedError()

    def new_level(self, props={}):
        """
        Triggered by the ui when the corresponding menu items are clicked.
        It opens a level configuration form in a tabbed widget, that calls it again
        with the properties ('props') filled by the user.
        """
        if self.project is None:
            Ui.instance().show_status('please create a project first.')
            return
        if props:
            self.project.new_level(props)
            Ui.instance().show_status('new level created')
        else:
            return Ui.instance().open_level_creation_dialog(self.new_level)

    def new_project(self, rootdir=None):
        if rootdir is None:
            rootdir = Ui.instance().select_directory('/tmp')
        if not os.path.exists(rootdir):
            os.makedirs(rootdir)

        print 'Weld.new_project in ', rootdir
        project = Project(rootdir)

        project.save()
        self.project = project
        self.current_project_path = rootdir
        Ui.instance().set_resources_draggable(True)
        Ui.instance().show_status('new project created')

    def on_item_dropped(self, url):
        """
        triggered when an item is dropped in the qsteelwidget.
        """
        print 'Weld.on_item_dropped:', url
        #make sure all struct are present
        if not(self.project and self.project.level):
            print >> sys.stderr, 'too early to drop: create a project and a level first.'
            return
        #retrieve data if it comes from weld
        if url in self.resMan:
            props = self.resMan.file_props(url)
            url = self.project.level.resMan.add_resource(props)
        #instanciate it
        if url in self.project.level.resMan:
            props = self.project.level.resMan.file_props(url)
            dtp=self.project.level.qsteelwidget.dropTargetPosition(Config.instance().drop_target_vec)
            props['position'] = dtp
            props['rotation']=self.project.level.qsteelwidget.dropTargetRotation()
            self.project.level.instanciate(props)
            s = 'dropped inanimate \'%s\' with id %i' % (props['name'], props['id'])
            print s
            Ui.instance().show_status(s)

    def open_project(self, rootdir=None, filename=None):
        if None in [rootdir, filename]:
            if rootdir is None:
                rootdir = '/tmp'
            filepath = Ui.instance().select_file(startdir=rootdir,
                                                 extensions='Weld project files (*.wp)',
                                                 label='Select a weld project')
            if filepath is None:
                Ui.instance().show_status('project opening is aborted')
                return
            rootdir, filename = os.path.split(filepath)
        else:
            if not os.path.exists(rootdir):
                self.current_project_path = None
                print >> sys.stderr, 'invalid project path:', rootdir
                return

        print 'Weld.open_project', filename, 'in', rootdir
        project = Project(rootdir)
        project.load()

        self.project = project
        self.current_project_path = rootdir
        Ui.instance().set_resources_draggable(True)
        Ui.instance().show_status('project %s opened' % (filename))

    def on_quit(self):
        print 'Weld.on_quit()'
        self.save()
        self.save_project()
        self.save_level()
        if self.project:
            self.project.close()

    def save_level(self):
        if self.project and self.project.level:
            print 'Weld.save_level()'
            self.project.level.save()
            Ui.instance().show_status('level saved.')
        else:
            Ui.instance().show_status('no level to save.')

    def save_project(self):
        if self.project is not None:
            print 'Weld.save_project()'
            self.project.save()
            Ui.instance().show_status('project saved.')
        else:
            Ui.instance().show_status('no project to save.')

    def run(self):
        r = Ui.instance().show()
        self.on_quit()
        return r



