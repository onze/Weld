import os.path
import sys

import config
import os
import shutil
from PySide import QtCore
from PySide import QtGui
from PySide.QtCore import Qt
from config import Config
from debug import curr_f
from debug import pp
from ui.ui import Ui

class ResourceManager:
    """
    Represents the system of resources that can be loaded in a level.
    """
    base_dirs = ['meshes', 'materials']
    def __init__(self, base_path):
        self.base_path = os.path.abspath(base_path)
        self.model = QtGui.QFileSystemModel()
        self.model.setRootPath(self.base_path)
        print 'ResourceManager started with root', self.base_path

    def __contains__(self, _url):
        """
        Returns True if the pointed file can be considered a resource, that is if
        the given url points to a file contained in one of base_path subdirs.
        """
        try:
            url = str(_url)
            url = url[len('file://'):]
        except:
            print type(url)
            print >> sys.stderr, 'in', curr_f(), 'url must be an url:', url
            return False

        if not os.path.exists(url):
            print >> sys.stderr, 'in', curr_f(), 'url does not exist:', url
            return False

        relpathdir, filename = os.path.split(os.path.relpath(url, self.base_path))
        if relpathdir.split(os.sep)[0] in ResourceManager.base_dirs:
            return True
        else:
            print 'relpathdir:', relpathdir
        return False

    
    def attach_to_Ui(self, tree):
        """
        populates the ui resources browser with the model. Resources are
        contained in a filesystem structure, so a treeview is used.
        """
        tree.setModel(self.model)
        tree.setRootIndex(self.model.index(self.model.rootPath()));

        #make it look a bit more like a resources browser
        tree.hideColumn(2)
        tree.hideColumn(3)
        tree.sortByColumn(0, Qt.AscendingOrder)
        #expand main categories
        dir = self.model.rootDirectory()
        dir.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        for entry in dir.entryInfoList():
            index = self.model.index(self.model.rootDirectory().path() + '/' + entry.fileName())
            tree.setExpanded(index, True)
        tree.setRootIsDecorated(False)
        tree.header().setResizeMode(QtGui.QHeaderView.ResizeToContents)

    def add_resource(self, srcpath, props):
        """
        Retrieve into base_path the file descripted by the given props, as well
        as each file it may depends on, according to these rules:
        - <filename>.mesh files depend on <filename>.material

        Returns the full url to the new resource, if any.
        """
        dep = {
            'mesh':['mesh', 'material'],
        }

        if props['ext'] not in dep:
            print curr_f(), ': no recorded dependencies for extension \'%s\'.' % props['ext']
            return

        #counts the number of dependencies retrived
        cnt = 0
        for ext in dep[props['ext']]:
            dir = Config.instance().resource_ext_to_dirs[ext]

            filename = props['name'] + '.' + ext
            src = os.path.join(srcpath, dir, filename)
            dst = os.path.join(self.base_path, dir, filename)
            
            cnt += self.retrieve_resource(src, dst)
        
        if cnt == len(dep[props['ext']]):
            new_props=dict(props)
            new_props['url']='file://' + os.path.join(self.base_path,
                                            Config.instance().resource_ext_to_dirs[props['ext']],
                                            props['name'] + '.' + props['ext'])
            return new_props
        return {}

    def file_props(self, url):
        """
        Takes the url to a file, and returns a dict of properties relative to it:
        """
        if url not in self:
            print url
            print >> sys.stderr, curr_f(), 'can only get props of contained files.'
            return None

        url = str(url[len('file://'):])
        
        props = {}
        #base url
        props['url'] = url
        #full path, relative to base_path
        props['relpath'] = os.path.split(os.path.relpath(url, self.base_path))[0]
        #name of th file
        s = os.path.split(url)[1].split('.')
        props['name'], props['ext'] = '.'.join(s[:-1]), s[-1]

        try:
            #type of resource, as defined in steel (inanimate, b-shape, behavior, etc)
            props['resource_type'] = props['relpath'].split(os.sep)[0]
        except:
            print 'url:', url
            print 'props:', props
            raise
        return props

    def retrieve_resource(self, src, dst):
        """
        Tries to copy src to dst, and return true if this was possible.
        Copy is skipped if src and dst timestamps are the same.
        """
        print 'ResourceManager.retrieve_resource:', src,'to',dst
        if not os.path.exists(src):
            return False

        dir = os.path.split(dst)[0]

        if os.path.exists(dir):
            if os.path.exists(dst):
                tt_dst = os.path.getmtime(dst)
                tt_src = os.path.getmtime(src)
                if tt_src < tt_dst:
                    return True
        else:
            os.makedirs(dir)
        #print 'copying', src, 'to', dst,
        shutil.copyfile(src, dst)
        #print 'done'
        return True


