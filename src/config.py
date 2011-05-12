
import os
from PySide.QtCore import qDebug

try:
    import weld_conf as conf
except IOError, e:
    print 'could not find config file \'weld_conf.py\'.'
    #setup default conf
    class conf:pass
    conf.data_path = 'data'
    conf.resources_root_path = 'resources'

class Config:
    """
    Proxy between the weld and its configuration file.
    """
    def __init__(self):
        self.resources_root_path=os.path.join(conf.data_path,conf.resources_root_path)
    

        
        

