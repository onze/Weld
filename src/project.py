import os.path

import os
import sys
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
        Ui.instance()._project_name=self.name
        Savable.__init__(self, savepath=os.path.join(rootdir,self.name + '.wp'))

        self.level = None
        self.level_name = None

        #
        self.savelist += ['rootdir','name','level_name']

    def load(self):
        Savable.load(self)
        if self.level_name is not None:
            self.load_level(self.level_name)

    def load_level(self,name):
        levelpath = os.path.join(self.rootdir, 'levels', name)
        level = Level(name,levelpath)
        level.load()
        level.attach_to_Ui()
        self.level_name=level.name
        self.level=level

    def save(self):
        Savable.save(self)

    def new_level(self, props):
        name = props['name']
        levelpath = os.path.join(self.rootdir, 'levels', name)
        try:
            os.makedirs(levelpath)
        except:pass
        level = Level(name, levelpath)
        level.attach_to_Ui()
        self.level_name=level.name
        self.level=level



















