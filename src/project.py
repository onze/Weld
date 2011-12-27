import sys

import debug
import os
from config import Config
from debug import curr_f
from level import Level
from savable import Savable
from ui.ui import Ui

class Project(Savable):
    file_extension = '.wp'
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
        Savable.__init__(self, savepath=os.path.join(rootdir, self.name + Project.file_extension))

        self.level = None
        self.level_name = None

        # list of commands (as custom strings to execute at next call to on_steel_ready)
        self.on_steel_ready_actions = []
        #
        self.savelist += ['rootdir', 'name', 'level_name']

    def __repr__(self):return self.__str__()
    def __str__(self):return '<Project %s>' % self.name

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
        self.close_level()

    def close_level(self):
        if self.level:
            self.level.close()

    def load(self):
        Savable.load(self)
        Ui.instance().project_name = self.name
        print debug.curr_f(), ': Config.on_project_opening_reopen_last_level = True'
        if Config.instance().on_project_opening_reopen_last_level:
            print 'trying to reopen level named \'%s\'' % (self.level_name)
            if self.level_name:
                self.open_level(self.level_name)
            else:
                print >> sys.stderr, 'could not reopen such level.'
        else:
            print 'level auto reload skipped.'

    def open_level(self, name):
        print '%(self)s.open_level(\'%(name)s\')' % locals()
        levelpath = os.path.join(self.rootdir, 'levels', name)
        if not os.path.exists(levelpath):
            s = 'Project.open_level(name=%s) canceled: invalid path %s' \
                % (name, levelpath)
            print >> sys.stderr, s
            return
        level = Level(self, name, levelpath)
        self.make_level_current(level)

    def new_level(self, props):
        print '%(self)s.new_level()' % locals()
        name = props['name']
        levelpath = os.path.join(self.rootdir, 'levels', name)
        try:
            os.makedirs(levelpath)
        except:
            raise
        level = Level(self, name, levelpath)
        self.make_level_current(level)

    def make_level_current(self, level):
        """
        Links the level with the editor (the widget part).
        """
        print '%(self)s.make_level_current()' % locals()
        if self.level is not None:
            if self.level is level:
                print 'current level is current already.'
                return
            self.close_level()
        self.level_name = level.name
        self.level = level
        self.on_steel_ready_actions.append('load_level')
        level.attach_to_Ui()

    def on_steel_ready(self, qsteelwidget):
        print "%(self)s.on_steel_ready()" % locals()
        Ui.instance().qsteelwidget.setRootDir(self.rootdir)
        if 0:
            while self.on_steel_ready_actions:
                action = self.on_steel_ready_actions[0]
                self.on_steel_ready_actions.pop(0)
                if 'load_level' in action:
                    assert(self.level is not None)
                    self.level.load()
                else:
                    raise Exception('%(self)s: unrecognized action in '\
                                    'self.on_steel_ready_actions: %(action)s' % \
                                    locals())
        if self.level is not None:
            self.level.on_steel_ready(qsteelwidget)

    def save_level(self):
        if self.level is not None:
            self.level.save()

    def save(self):
        Savable.save(self)
        if self.level is not None:
            self.level.save()



















