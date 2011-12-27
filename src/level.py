import os.path

__author__ = "onze"
__date__ = "$7-May-2011 7:48:35 PM$"

import os
import sys
from PySide import QtGui
from config import Config
from savable import Savable
from ui.ui import Ui
from resourcemanager import ResourceManager
from debug import pp
import weld

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
        # list of AgentId's (int's)
        self.agents = []
        self.camera_position = QtGui.QVector3D()
        self.camera_rotation = QtGui.QVector4D()
        self.resMan = None
        self.qsteelwidget = None

        Savable.__init__(self, savepath=os.path.join(self.path, self.name + '.lvl.weld'))
        self.savelist += ['camera_position', 'camera_rotation']
        self.resources = {'meshes':[]}


    def __repr__(self):return self.__str__()
    def __str__(self):return '<Level \'%s\'@%s>' % (self.name, self.path)

    def attach_to_Ui(self):
        """
        Links the level with its views.
        """
        print '<Level \'%s\'>.attach_to_Ui():' % (self.name)

        self.resMan = ResourceManager(self.path, level=self)
        self.resMan.attach_to_Ui(Ui.instance().res_browser['level'])
        
        self.qsteelwidget = Ui.instance().qsteelwidget
        if self.qsteelwidget.isSteelReady():
            print 'loading now.'
            weld.Weld.instance().on_steel_ready()
        else:
            print 'will wait for steel to be ready before loading.'
            self.qsteelwidget.onSteelReady.connect(weld.Weld.instance().on_steel_ready)
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
        if props['resource_type'] == 'meshes':
            self.resMan.inc_refcount(props)
            modelId = self.qsteelwidget.createOgreModel(props['meshName'] + '.' + props['ext'],
                                                        props['position'],
                                                        props['rotation'],
                                                        not already_in)
            print 'modelId: %(modelId)i' % locals()
            agentId = self.qsteelwidget.createAgent()
            print 'agentId: %(agentId)i' % locals()
            r = self.qsteelwidget.linkAgentToOgreModel(agentId, modelId)
            print 'could link: %s' % r
            props['agentId'] = agentId
            if not already_in:
                self.agents.append(dict(props))
        else:
            print >> sys.__stderr__, 'Level.instanciate(): unknown resource type'

    def on_steel_ready(self, qsteelwidget):
        """
        triggered by the qsteelwidget when steel is ready to process commands.
        """
        self.qsteelwidget = qsteelwidget
        print "<Level %s>.on_steel_ready()" % (self.name)
        self.resMan.qsteelwidget = self.qsteelwidget
        self.qsteelwidget.setLevel(self.project.rootdir, self.name)

        if self.camera_position != QtGui.QVector3D():
            self.qsteelwidget.cameraPosition(self.camera_position)
        if self.camera_rotation != QtGui.QVector4D():
            self.qsteelwidget.cameraRotation(self.camera_rotation)

    def load(self):
        """
        Overloads Savable.load, just to add sync with steel-sided level.
        """
        if self.qsteelwidget is not None:
            self.qsteelwidget.loadLevel()
        Savable.load(self)

    def save(self):
        """
        Retrieve some data before saving them.
        """
        self.camera_position = self.qsteelwidget.cameraPosition()
        self.camera_rotation = self.qsteelwidget.cameraRotation()
        Savable.save(self)
        if self.qsteelwidget.saveCurrentLevel():
            s='%(self)s saved successfuly'
        else:
            s='%(self)s failed to save'
        Ui.instance().show_status(s)


