
import os
from PySide.QtGui import QVector3D

try:
    import weld_conf as conf
except IOError, e:
    print 'could not find config file \'weld_conf.py\'.'

    #setup default conf
    #see weld_conf.py for documentation.
    class conf:
        debug = False

        weld_version='0.1.0'
        weld_data_path = 'data'
        weld_resource_group = 'weld_internals'
        weld_trash_folder = 'trash'

        BT_nodes_classes_names = [
            'BTSequence',
            'BTSelector',
            'BTTimeFilter',
            'BTLocalizer',
            'BTNavigator',
            'BTTimeFilter',
            'BTSensor',
            'BTOgreModelAnimator',
            'BTDecorator_NOT',
        ]
        BT_warn_for_unexpected_infofiles = True
        BT_add_debug_info_into_xml = True

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
        
        ################################levels
        on_project_opening_reopen_last_level = True

class Config:
    """
    Proxy between weld and its configuration file.
    """
    __instance = None
    def __init__(self):
        if Config.__instance is None:
            Config.__instance = self
        else:
            raise Exception('can\'t declare new Config instance. Config is a singleton.')
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
            s = 'there is no such config attribute as \'%s\'.' % (name)
            print s
            raise Exception(s)

    @staticmethod
    def instance():
        if Config.__instance is None:
            Config.__instance = Config()
        return Config.__instance
    

        
        

