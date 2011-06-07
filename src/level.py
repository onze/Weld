import os.path

__author__ = "onze"
__date__ = "$7-May-2011 7:48:35 PM$"

import os
from PySide import QtGui
from config import Config
from savable import Savable
from ui.ui import Ui
from resourcemanager import ResourceManager

class Level(Savable):

    def __init__(self, project, name, levelpath):
        """
        Holds material paths and keep the level browser sync with steel.
        params:
        name: level name
        levelpath: root path of resources used in the level (no sharing yet)
        """
        self.project = project
        self.name = name
        self.path = levelpath
        self.resMan=None

        Savable.__init__(self, savepath=os.path.join(levelpath, self.name + '.lvl'))
        self.resources = {'models':[]}

    def attach_to_Ui(self):
        """
        Links the level with its views.
        """
        print '<Level \'%s\'>.attach_to_Ui()' % (self.name)

        self.resMan=ResourceManager(self.path)
        self.resMan.attach_to_Ui(Ui.instance().res_browser['level'])
        
        self.qsteelwidget = Ui.instance().qsteelwidget
        Ui.instance().level_name = self.name
        #may have already been set, but there's no steel context to set it before
        #the first level is created
        self.qsteelwidget.setLevel(self.project.rootdir, self.name)
        
    def close(self):
        """
        cleanly closes resources taken by the level.
        """
        if self.qsteelwidget:
            self.qsteelwidget.close()

    def instanciate(self, props):
        """
        Make Steel instanciate an object according to the given props.
        """
        if props['resource_type'] == 'inanimate':
            id = self.qsteelwidget.drop_inanimate(props['name']+'.'+props['ext'], *Config.instance().drop_target_vec)
            print 'id:', id
            Ui.instance().show_status('dropped inanimate \'%s\' with id %i' % (props['name'], id))
        else:
            print 'unknown resource type'



