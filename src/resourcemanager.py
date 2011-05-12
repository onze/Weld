
import os

from PySide import QtGui

class ResourceManager:
    """
    Represents the system of resources that can be loaded in a level.
    The os filesystem is used for this: a root folder is needed at startup, then
    the manager acts as a proxy betweeen weld and the filesystem, where a resource
    category is a folder (subcategories are subfolders, etc), and files are resources.
    A resource file is a text file containing key=value informations.
    """
    def __init__(self,base_path):
        self.base_path=base_path
        self.model=QtGui.QFileSystemModel()
        base_path=os.path.join(os.getcwd(),base_path)
        print 'ResourceManager started with root',base_path
        self.model.setRootPath(base_path)
        





