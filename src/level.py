import os.path

__author__ = "onze"
__date__ = "$7-May-2011 7:48:35 PM$"

import os
from PySide import QtGui
from config import Config
from savable import Savable
from ui.ui import Ui
from resourcemanager import ResourceManager
from debug import pp

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
        self.inanimates = []
        self.camera_position=QtGui.QVector3D()
        self.camera_rotation=QtGui.QVector4D()
        self.resMan = None

        Savable.__init__(self, savepath=os.path.join(levelpath, self.name + '.lvl'))
        self.savelist += ['camera_position', 'camera_rotation', 'inanimates']
        self.resources = {'inanimate':[]}

    def attach_to_Ui(self):
        """
        Links the level with its views.
        """
        print '<Level \'%s\'>.attach_to_Ui():' % (self.name),

        self.resMan = ResourceManager(self.path)
        self.resMan.attach_to_Ui(Ui.instance().res_browser['level'])
        
        self.qsteelwidget = Ui.instance().qsteelwidget
        if self.qsteelwidget.isSteelReady():
            print 'loading now.'
            self.on_steel_ready()
        else:
            print 'will wait for steel to be ready before loading.'
            self.qsteelwidget.onSteelReady.connect(self.on_steel_ready)
        Ui.instance().level_name = self.name
        
    def close(self):
        """
        cleanly closes resources taken by the level.
        """
        if self.qsteelwidget:
            self.qsteelwidget.close()

    def instanciate(self, props, already_in=False):
        """
        Make Steel instanciate an object according to the given props.
        If already_in is set to False (default), the object is saved for reload.
        """
        print '<Level \'%s\'>.instanciate():\n%s' % (self.name, pp(props))
        if props['resource_type'] == 'inanimate':
            id = self.qsteelwidget.addInanimate(props['name'] + '.' + props['ext'],
                                                props['position'],
                                                props['rotation'])
            props['id'] = id
            if not already_in:
                self.inanimates.append(dict(props))
        else:
            print 'unknown resource type'

    def on_steel_ready(self):
        """
        triggered by the steelwidget when steel is ready to process commands.
        """
        print "<Level %s>.on_steel_ready()" % (self.name)
        self.qsteelwidget.setLevel(self.project.rootdir, self.name)
        for props in self.inanimates:
            print 'restoring', pp(props)
            self.instanciate(props, already_in=True)
        self.qsteelwidget.cameraPosition(self.camera_position)
        self.qsteelwidget.cameraRotation(self.camera_rotation)

    def save(self):
        """
        Retrieve some data before saving them.
        """
        self.camera_position=self.qsteelwidget.cameraPosition()
        self.camera_rotation=self.qsteelwidget.cameraRotation()
        Savable.save(self)


