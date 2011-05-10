# To change this template, choose Tools | Templates
# and open the template in the editor.

__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

from ui.ui import Ui
from level import Level

class Weld(object):
    def __init__(self, parent=None):
        self.ui=Ui(self)

        #setup internal resource handlers
        self.level=None

        #ready
        self.ui.show_status('ready', 1000)

        #debug
        self.new_level()

    def unload_level(self):
        self.level.unload()
        self.level=None

    def new_level(self):
        if self.level:
            self.unload_level()
        self.level=Level()
        
        self.ui.add_engine_view(self.level.name)
        self.ui.feed_resources(self.level.resources)

    def run(self):
        return self.ui.show()



