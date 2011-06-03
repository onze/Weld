
__author__ = "onze"
__date__ = "$7-May-2011 7:48:35 PM$"

import os
from savable import Savable
from ui.ui import Ui

class Level(Savable):

    def __init__(self, name, levelpath):
        """
        Holds material paths and keep the level browser sync with steel.
        params:
        name: level name
        levelpath: root path of resources used in the level (no sharing yet)
        """
        self.name = name
        self.path = levelpath
        Savable.__init__(self, savepath=os.path.join(levelpath, self.name + '.lvl'))


    def attach_to_Ui(self):
        """
        Links the level with its views.
        """
        self.browser = Ui.instance().res_browser['level']
        model=self.browser.model()
        model.setRootPath(self.path)
        self.browser.setRootIndex(model.index(model.rootPath()));

        self.qsteelwidget = Ui.instance().qsteelwidget
        Ui.instance().level_name=self.name


