import os.path
import sys

import os
from debug import curr_f
from level import Level
from savable import Savable
from ui.ui import Ui

class Project(Savable):
    def __init__(self, rootdir):
        """
        rootdir: path to the root folder of the project. The project holds the
        directory name.
        """
        if not os.path.exists(rootdir):
            raise Exception('path %s does not exist.')
        self.rootdir = rootdir
        self.name = os.path.split(rootdir)[-1]
        Ui.instance()._project_name = self.name
        Savable.__init__(self, savepath=os.path.join(rootdir, self.name + '.wp'))

        self.level = None
        self.level_name = None

        #
        self.savelist += ['rootdir', 'name', 'level_name']

    def add_resource(self, props):
        """
        Adds a resource to the level under edition.
        """
        #TODO: add resource sharing between levels.
        if self.level is None:
            print >> sys.stderr, debug.curr_f(), ': no current level defined yet.'
            return
        {'inanimate':Level.load_inanimate}[props['resource_type']](self.level, props)

    def close(self):
        """
        cleanly closes resources taken by the project.
        """
        if self.level:
            self.level.close()

    def load(self):
        Savable.load(self)
        Ui.instance().project_name = self.name
        if self.level_name:
            self.open_level(self.level_name)

    def open_level(self, name):
        print '<Project \'%s\'>.open_level(\'%s\')'%(self.name,name)
        levelpath = os.path.join(self.rootdir, 'levels', name)
        if not os.path.exists(levelpath):
            print>>sys.stderr,'Project.open_level(name=%s) canceled: invalid path %s'%(name,levelpath)
            return
        level = Level(self, name, levelpath)
        level.load()
        level.attach_to_Ui()
        self.level_name = level.name
        self.level = level

    def save(self):
        Savable.save(self)

    def new_level(self, props):
        name = props['name']
        levelpath = os.path.join(self.rootdir, 'levels', name)
        try:
            os.makedirs(levelpath)
        except:pass
        level = Level(self, name, levelpath)
        level.attach_to_Ui()
        self.level_name = level.name
        self.level = level



















