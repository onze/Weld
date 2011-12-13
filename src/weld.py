import os.path

# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

from config import Config
import os
import sys
import user
from PySide import QtCore, QtGui
from level import Level
from project import Project
from resourcemanager import ResourceManager
from btmanager import BTManager
from ui.ui import Ui
from savable import Savable
from debug import pp, curr_f

class Weld(Savable):
    """
    Main class of the editor.
    """
    #singleton
    __instance = None

    def __init__(self, parent=None):
        if Weld.__instance is None:
            Weld.__instance = self
        else:
            raise Exception('can\'t declare new Weld instance. Weld is a singleton.')
        Savable.__init__(self, savepath=os.path.join(user.home, '.weld', 'weld.cache'))
        self.savelist += ['current_project_path']
        # this is used to reload last opened project
        self.current_project_path = None

        Ui(self)

        # setup internal resource handlers
        self.project = None
        
        # list of resources we can ask steel to load
        self.resMan = ResourceManager(os.path.join(Config.instance().weld_data_path, 'resources'))
        self.resMan.attach_to_Ui(Ui.instance().res_browser['library'])

        # entity responsible for behavior trees manipulations
        self.BTMan = BTManager()

        # ready
        Ui.instance().show_status('ready', 1000)
        self.load()
        if Config.instance().on_weld_start_reopen_last_project:
            if self.current_project_path is not None:
                print 'auto reopening project \'%s\'.' % self.current_project_path
                p, f = os.path.split(self.current_project_path)
                self.open_project(self.current_project_path, f)
            else:
                print 'no project to reopen.'
        else:
            print 'skipping project reopening.'

    def BT_export(self):
        """
        Called by the Ui. Exports filesystem BT into Steel readable files.
        """
        src = os.path.join(self.resMan.base_path, Config.instance().weld_BT_root_folder)
        dst = os.path.join(self.project.rootdir, Config.instance().weld_BT_root_folder)
        #this operation has lots of exceptions to output...
        try:
            self.BTMan.export(src, dst)
        except Exception, e:
            print >> sys.__stderr, 'ERROR in Weld.BT_export():'
            print >> sys.__stderr, e.args[0]
            print >> sys.__stderr, 'export cancelled (some cleanup might be needed in %s)' % dst

    def close_project(self):
        Ui.instance().set_resources_draggable(False)
        raise NotImplementedError()

    def export_level(self, levelname=None):
        """
        Export the given level (not implemented yet).
        If no level is given, the current one is.
        """
        if levelname is None:
            if self.project is None:
                s = 'no project is opened.'
                print s
                Console.write(s)
                return
            if self.project.level is None:
                s = 'current project has no current level to export.'
                print s
                Console.write(s)
                return
            self.project.level.export()
        else:
            raise NotImplementedError()

    @staticmethod
    def instance():
        if Weld.__instance is None:
            raise Exception('weld instance is None ? Oo')
        return Weld.__instance

    def new_level(self, props={}):
        """
        Triggered by the ui when the corresponding menu item is clicked.
        It opens a level configuration form in a tabbed widget, that calls it
        again with the properties ('props') filled by the user.
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
        """
        Open a new project.
        If rootdir is given, directly open the project file (see 
        Project.file_extension)") located in it.
        Otherwise, open a dialog for the user to choose a path.
        """
        if rootdir is None:
            rootdir = Ui.instance().select_directory(user.home)
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
            print >> sys.stderr, 'it\'s too early to drop stuff: '\
            'create a project and a level first !'
            return

        #retrieve data if it comes from weld
        if url in self.resMan:
            props = self.resMan.file_props(url)
            if props is None:
                print >> sys.stderr, curr_f(), ': url(\'%s\') in self.resMan '\
                    'but can\'t retrieve props.' % (url)
                return
            props = self.project.level.resMan.add_resource(self.resMan.base_path,
                                                           props)
            url = props['url']
            if props == {} or url not in self.project.level.resMan:
                print >> sys.stderr, curr_f(), 'could not retrieve file and/or '\
                    'dependencies for props:', pp(props)
                return

        #instanciate it
        if url in self.project.level.resMan:
            props = self.project.level.resMan.file_props(url)
            dtp = self.project.level.qsteelwidget.dropTargetPosition(Config.instance().drop_target_vec)
            props['position'] = dtp
            props['rotation'] = self.project.level.qsteelwidget.dropTargetRotation()
            if props['resource_type'] == 'meshes':
                props['meshName'] = props['name']
                self.project.level.instanciate(props)
                s = 'dropped agent \'%s\' with id %i' % (props['name'], props['id'])
                print s
                Ui.instance().show_status(s)
            else:
                Ui.instance().show_status('can only drop meshes so far')

    def open_project(self, rootdir=None, filename=None):
        """
        root dir is the path to the project, filename is the project file.
        """
        if None in [rootdir, filename]:
            if rootdir is None:
                rootdir = '~'
            filepath = Ui.instance().select_file(startdir=rootdir,
                                                 extensions='Weld project files (*%s)' % Project.file_extension,
                                                 label='Select a weld project')
            if filepath is None:
                Ui.instance().show_status('project opening is aborted')
                return
            rootdir, filename = os.path.split(filepath)
        else:
            if not os.path.exists(rootdir):
                self.current_project_path = None
                s = 'invalid project path:', rootdir
                print >> sys.stderr, s
                Ui.instance().show_status(s)
                return
            if not os.path.exists(os.path.join(rootdir, filename + Project.file_extension)):
                self.current_project_path = None
                s = 'can\'t locate project file \'%s\' inside \'%s\'' % (filename, rootdir)
                print >> sys.stderr, s
                Ui.instance().show_status(s)
                return

        print 'Weld.open_project \'%(filename)s in %(rootdir)s' % locals()
        project = Project(rootdir)
        project.load()

        self.project = project
        self.current_project_path = rootdir
        Ui.instance().set_resources_draggable(True)
        Ui.instance().show_status('project %s opened' % (filename))

    def on_steel_closing(self, qsteelwidget):
        p = os.path.join(self.current_project_path, 
                         Config.instance().weld_data_path,
                         'editor')
        qsteelwidget.removeResourceLocation(p,
                                            Config.instance().weld_resource_group)

    def on_steel_ready(self):
        print "Weld.on_steel_ready()"
        qsteelwidget=Ui.instance().qsteelwidget
        #make sure we know when to clean what follows
        qsteelwidget.onSteelClosing.connect(self.on_steel_closing)
        #add editing specific resources location
        p = os.path.join(self.current_project_path, 
                         Config.instance().weld_data_path,
                         'resources')
        qsteelwidget.addResourceLocation(p, 
                                         'FileSystem',
                                         Config.instance().weld_resource_group)
        if self.project is not None:
            self.project.on_steel_ready(qsteelwidget)

    def on_agents_selected(self, agentIds):
        print 'Weld.on_agents_selected() ids:', agentIds

    def on_quit(self):
        print 'Weld.on_quit()'
        self.save()
        self.save_project()
        if self.project:
            self.project.close()

    def save_level(self):
        """
        might be called by the ui.
        """
        if self.project is not None:
            self.project.save_level()

    def save_project(self):
        if self.project is None:
            Ui.instance().show_status('no project to save.')
        else:
            print 'Weld.save_project()'
            self.project.save()
            Ui.instance().show_status('project saved.')

    def run(self):
        r = Ui.instance().show()
        self.on_quit()
        return r



