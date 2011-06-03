
import os

try:
    import weld_conf as conf
except IOError, e:
    print 'could not find config file \'weld_conf.py\'.'
    #setup default conf
    class conf:pass
    conf.debug=False
    conf.weld_data_path = 'data'
    conf.project_data_path = 'data'

class Config:
    """
    Proxy between the weld and its configuration file.
    """
    def __init__(self):
        #forst do abasic copy of the config
        for k,v in conf.__dict__.items():
            self.__dict__[k]=v

        #TODO: then treat special cases here

    def __getattr__(self,name):
        if name in self.__dict__:
            #TODO: insert special cases here
            return self.__dict__[name]
        else:

            raise Exception('there is no such config attribute as \'%s\'. Config dump:%s'%(name,self.__dict__))
    

        
        

