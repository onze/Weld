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
        self.things = []
        self.camera_position = QtGui.QVector3D()
        self.camera_rotation = QtGui.QVector4D()
        self.resMan = None

        Savable.__init__(self, savepath=os.path.join(levelpath, self.name + '.lvl'))
        self.savelist += ['camera_position', 'camera_rotation', 'things']
        self.resources = {'meshes':[]}

    def attach_to_Ui(self):
        """
        Links the level with its views.
        """
        print '<Level \'%s\'>.attach_to_Ui():' % (self.name),

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
            id = self.qsteelwidget.createThing(props['meshName'] + '.' + props['ext'],
                                               props['position'],
                                               props['rotation'],
                                               not already_in)
            props['id'] = id
            if not already_in:
                self.things.append(dict(props))
        else:
            print >> sys.__stderr__, 'Level.instanciate(): unknown resource type'

    def on_steel_ready(self):
        """
        triggered by the steelwidget when steel is ready to process commands.
        """
        print "<Level %s>.on_steel_ready()" % (self.name)
        self.resMan.qsteelwidget = self.qsteelwidget
        self.qsteelwidget.onThingUpdated.connect(self.on_thing_updated)
        self.qsteelwidget.onThingsDeleted.connect(self.on_things_deleted)
        self.qsteelwidget.setLevel(self.project.rootdir, self.name)
        for props in self.things:
            print "restoring:"
            self.instanciate(props, already_in=True)
        if self.camera_position != QtGui.QVector3D(.0, .0, .0):
            self.qsteelwidget.cameraPosition(self.camera_position)
        if self.camera_rotation != QtGui.QVector4D(.0, .0, .0, .0):
            self.qsteelwidget.cameraRotation(self.camera_rotation)
        weld.Weld.instance().on_steel_ready(self.qsteelwidget)

    def on_things_deleted(self, ids):
        to_delete = [i for i, t in enumerate(self.things) if t['id'] in ids]
        while to_delete:
            self.resMan.dec_refcount(self.things[to_delete[0]])
            del self.things[to_delete[0]]
            to_delete.pop(0)

    def on_thing_updated(self, id, property, value):
        for thing in self.things:
            if thing['id'] == id:
                if property in thing:
                    thing[property] = value
                else:
                    print >> sys.__stderr__, 'ERROR in on_thing_updated(self, id=%i, \
property=%s, value=%s): unknown property. skipping' % (id, property, str(value))
                break

    def save(self):
        """
        Retrieve some data before saving them.
        """
        self.camera_position = self.qsteelwidget.cameraPosition()
        self.camera_rotation = self.qsteelwidget.cameraRotation()
        Savable.save(self)


