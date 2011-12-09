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
        #TODO:use a dict [id:{props}]
        self.agents = []
        self.camera_position = QtGui.QVector3D()
        self.camera_rotation = QtGui.QVector4D()
        self.resMan = None
        self.qsteelwidget = None

        Savable.__init__(self, savepath=os.path.join(self.path, self.name + '.weld.lvl'))
        self.savelist += ['camera_position', 'camera_rotation', 'agents']
        self.resources = {'meshes':[]}

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '<Level \'%s\'@%s>' % (self.name, self.path)

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
        if props['resource_type'] == 'meshes':
            self.resMan.inc_refcount(props)
            id = self.qsteelwidget.createAgent(props['meshName'] + '.' + props['ext'],
                                               props['position'],
                                               props['rotation'],
                                               not already_in)
            props['id'] = id
            if not already_in:
                self.agents.append(dict(props))
        else:
            print >> sys.__stderr__, 'Level.instanciate(): unknown resource type'

    def on_steel_ready(self):
        """
        triggered by the qsteelwidget when steel is ready to process commands.
        """
        print "<Level %s>.on_steel_ready()" % (self.name)
        self.resMan.qsteelwidget = self.qsteelwidget
        self.qsteelwidget.onAgentUpdated.connect(self.on_agent_updated)
        self.qsteelwidget.onAgentsDeleted.connect(self.on_agents_deleted)
        self.qsteelwidget.setLevel(self.project.rootdir, self.name)
        if len(self.agents):
            for props in self.agents:
                print "restoring:"
                self.instanciate(props, already_in=True)
        else:
            print 'no agent to restore.'
        if self.camera_position != QtGui.QVector3D():
            self.qsteelwidget.cameraPosition(self.camera_position)
        if self.camera_rotation != QtGui.QVector4D():
            self.qsteelwidget.cameraRotation(self.camera_rotation)
        weld.Weld.instance().on_steel_ready(self.qsteelwidget)

    def on_agents_deleted(self, ids):
        to_delete = [i for i, t in enumerate(self.agents) if t['id'] in ids]
        while to_delete:
            self.resMan.dec_refcount(self.agents[to_delete[0]])
            del self.agents[to_delete[0]]
            to_delete.pop(0)

    def on_agent_updated(self, id, property, value):
        for agent in self.agents:
            if agent['id'] == id:
                if property in agent:
                    agent[property] = value
                else:
                    print >> sys.__stderr__, 'ERROR in on_agent_updated(self, id=%i, \
property=%s, value=%s): unknown property. skipping' % (id, property, str(value))
                break

    def save(self):
        """
        Retrieve some data before saving them.
        """
        self.qsteelwidget.saveCurrentLevel()
        self.camera_position = self.qsteelwidget.cameraPosition()
        self.camera_rotation = self.qsteelwidget.cameraRotation()
        Savable.save(self)


