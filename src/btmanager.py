
import os.path
import sys
import time

import debug
import glob
import os
from config import Config
import weld

class BTManager(object):
    """
    Just to make it clear, the info_file is the file inside a folder that
    contains its node's description.
    """

    def __init__(self):
        pass

    def export(self, src_path, dst_path):
        """
        Compiles each BT (whose name matches en entry in 'names', if given) from
        the source folder path to the dest one.
        """
        # used in debug mode, to add path of info_files into xml representations
        self.src_path = src_path
        print 'BTManager.export()',

        # skip folders starting with '__'
        path, name = os.path.split(src_path)
        if name.startswith('__'):
            print name, 'is a skippable __folder: skipping it.'
            return

        print 'from  %(src_path)s  to  %(dst_path)s' % locals()
        if not os.path.exists(src_path):
            print >> sys.stderr, 'in BTManager.export(): src folder does not exist:', src_path
            return
        
        if not os.path.exists(dst_path):
            print 'creating dst folder', dst_path
            os.makedirs(dst_path)

        # metadata
        import datetime
        serialization = {
        'weld_version':weld.Weld.version,
        'date':time.strftime('%Y-%m-%d_%H:%M:%S')
        }
        
        serialization['BT_root'] = self.serialize_node(src_path)

        dst = os.path.join(dst_path, name)
        print 'writing to', dst
        self.save_string_to(str(serialization), dst)
            

    def serialize_node(self, fullpath):
        """
        Recursively walks a directory, outputting a dict representation of the BT.
            - fullpath: rootpath of the BT (the dir name its info_file is in)
        """
        node_content = {}
        if Config.instance().BT_serialization_add_debug_info:
            node_content.update({
                                '__src_fullpath':fullpath,
                                })

        ifile_fullpath = self.get_ifile(fullpath)
        if not ifile_fullpath:
            # this code path is used when the current BT node has no description.
            # it could be replaced by a dummy node, but I think it is wiser to
            # raise an exception as soon as possible, to warn the developper
            raise Exception('in BTManager.serialize_node(): missing info file '\
                            'for node %(fullpath)s' % locals())

        path, name = os.path.split(fullpath)
        # get dict of info_file content
        d = self.ifile2dict(ifile_fullpath, parent_dirname=name)
        # assert no attribute have same name between node's original dict and its
        # info_node's dict.
        if len(set(d.keys()).intersection(set(node_content.keys()))):
            s = 'in BTManager.serialize_node(%(path)s, %(name)s):\n' \
                'a key BT node\'s original dict would be overwritten by '\
                'info_file content. Original dict:%(node_content)s\n'\
                'info_file content:%(d)s' % locals()
            raise Exception(s)
        node_content.update(d)

        # now node is complete, except for its child nodes.
        # insert descriptions of child nodes.
        children = [self.serialize_node(child_fullpath) \
            for child_fullpath in self.get_subdirs(fullpath)]
        if children:
            node_content['children'] = children
        else:
            #print debug.pp(node_content)
            pass
        return node_content

    def ifile2dict(self, ifile_fullpath, parent_dirname='unknown'):
        """
        Returns a dict of the attributes contained in the info_file pointed
        by the given fullpath.
        """
        print 'ifile2dict on', ifile_fullpath

        # print 'ifile2xml() on ', ifile_fullpath
        ifile_path, ifile_name = os.path.split(ifile_fullpath)
        
        # once again, make sure the requested class exists
        if not ifile_name in (Config.instance().BT_nodes_classes_names \
                              #+ Config.instance().BT_leaves_classes_names\
                              ):
            s = 'in BTManager.ifile2dict(): unrecognized class \'%s\''
            raise Exception(s % ifile_name)

        with open(ifile_fullpath) as file:
            lines = map(str.strip, file.readlines())
        # skip empty lines
        lines = [line for line in lines
            if line]

        # skip comments
        lines = [line for line in lines
            if not (line.startswith('#') or line.startswith('//'))]

        content = {
            'class':ifile_name,
        }
        
        if lines:
            # split attribute names and values
            splits = [([line, 'True'], line.split('='))[int('=' in line)]
                for line in lines]
            attributes, values = zip(*[(split[0], '='.join(split[1:]))
                                     for split in splits])
            
            # make sure no attr starts with '__'
            for attr in attributes:
                if attr.startswith('__'):
                    s = 'WARNING: in BTManager.ifile2dict(ifile_fullpath=%(ifile_fullpath)s, '\
                        'parent_dirname=%(parent_dirname)s):\nattributes\' names '\
                        'starting with \'__\' are not recommended.'
                    print >> sys.__stderr__, s

            # interpret values as python values if possible
            def cast_or_str(v):
                try:return ast.literal_eval(v)
                except:return v
            values = map(cast_or_str, values)

            content.update(dict(zip(attributes, values)))

        if Config.instance().BT_serialization_add_debug_info:
            content['__parent_dir_name'] = parent_dirname
            content['__ifile_path'] = ifile_path
            content['__ifile_name'] = ifile_name

        return content

    def save_string_to(self, s, fullpath):
        """
        Write the given string at the given location.
        """
        #print 'BTManager.save_string_to(%s)' % fullpath
        with open(fullpath, 'w') as f:
            f.write(s)

    def get_subdirs(self, path):
        """
        Takes a path and returns all valid folders at its first level.
        A inode is not a valid BT node if it is not a directory or link, or if
        its name starts with 2 underscores.
        """
        return sorted([f for f in glob.glob(os.path.join(path, '*')) \
                      if os.path.isdir(f) and \
                      not os.path.split(f)[1].startswith('__')
                      ])

    def get_ifile(self, dir_fullpath):
        """
        Takes a path and returns the first filepath that fits info_files criteria:
            - its name is a BT class name
            - it does not start with __
        That's it.
        """
        # print 'get_ifile at', dir_fullpath
        for fullpath in glob.glob(os.path.join(dir_fullpath, '*')):
            # skip folders
            if not os.path.isfile(fullpath):
                continue
            path, name = os.path.split(fullpath)
            # skip info files that are not recognized, and warn about them
            if name not in (Config.instance().BT_nodes_classes_names \
                            # +Config.instance().BT_leaves_classes_names \
                            ):
                if Config.instance().BT_warn_for_unexpected_infofiles:
                    print 'WARNING: in BTManager.get_ifile(%s): ' \
                        'unrecognized BT class: %s. Not using this file.' \
                        % (dir_fullpath, name)
                continue
            return fullpath
        return None

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print   'usage: python btmanager.py src_path [src_path, ...] dst_path'\
            '\nbtmanager.py can be used to manually export filesystem BTrees to '\
            'Steel.'
    else:
        if sys.argv[1] in ['d', 'def', 'default']:
            src_paths = ['/media/z2/python/1105/Weld/src/data/resources/BT']
            dst_path = '/media/z2/python/1105/weld_testing_folder/BT'
        else:
            src_paths = sys.argv[1:-1]
            dst_path = sys.argv[-1]
        btman = BTManager()
        for src_path in src_paths:
            btman.export(src_path, dst_path)
