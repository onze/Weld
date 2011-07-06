
import os
from PySide.QtGui import QVector3D

try:
    import weld_conf as conf
except IOError, e:
    print 'could not find config file \'weld_conf.py\'.'

    #setup default conf
    class conf:
        debug = False

        weld_data_path = 'data'
        weld_resource_group = 'weld_internals'
        weld_trash_folder='trash'

        resource_ext_to_dirs = {
            'mesh':'meshes',
            'material':'materials'
        }
        res_dep = {
            'mesh':['mesh', 'material', 'png'],
        }

        show_ogre_init = False
        drop_target_vec = (.0, -1., -10.)

        project_data_path = 'data'

class Config:
    """
    Proxy between weld and its configuration file.
    """
    __instance = None
    def __init__(self):
        if Config.__instance is None:
            Config.__instance=self
        else:
            raise Exception('can declare new Config instance. Config is a singleton.')
        #first do a basic copy of the config
        for k, v in conf.__dict__.items():
            self.__dict__[k] = v

        #TODO: then treat special cases here
        self.drop_target_vec = QVector3D(*self.drop_target_vec)

    def __getattr__(self, name):
        if name in self.__dict__:
            #TODO: insert special cases here
            return self.__dict__[name]
        else:
            raise Exception('there is no such config attribute as \'%s\'. Config dump:%s' % (name, dir(self)))

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config.__instance = Config()
        return Config.__instance
    

        
        

