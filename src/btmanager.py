import os.path
import sys

import glob
import os
from config import Config
from ui.console import Console
from ui.ui import Ui

class BTManager(object):

    #4 spaces indentation, like in python
    xml_indent_unit='  '

    def __init__(self):
        pass

    def export(self, src_path, dst_path, names=[]):
        """
        Compiles each BT whose name matches 'names' from the source folder path
        to the dest one.
        """
        #used in debug mode, to add path of info_files into xml representations
        self.src_path = src_path
        print 'BTManager.export()  from  %s  to  %s' % (src_path, dst_path)
        if not os.path.exists(src_path):
            print >> sys.stderr, 'in BTManager.export(): src folder does not exist:', src_path
            return
        if not os.path.exists(dst_path):
            print 'creating dst folder', dst_path
            os.makedirs(dst_path)
        fullpaths = self.get_subdirs(src_path)
        for fullpath in fullpaths:
            path, name = os.path.split(fullpath)
            #only export trees that are requested
            if name not in names:
                continue
            prefix = '<?xml version="1.0" encoding="UTF-8" ?>\n'
            xmlstring = prefix + self.BT2xml(path, name)
            self.save_string_to(xmlstring, os.path.join(dst_path, name + '.xml'))

    def BT2xml(self, rootpath, name, depth=0):
        """
        Recursively walks a directory, outputting an xml representation of the BT.
            - path: rootpath of the BT
            - name: BT name.
        For instance, if one wants to get the xml a a BT called myBT, which is
        localized inside /path/to/my_bts, myBT would be the name and /path/to/my_bts
        the rootpath.
        """
        #print ('\t' * depth) +'BT2xml in', name, '(', rootpath, ')'
        ifile_fullpath = self.get_ifile(os.path.join(rootpath, name))
        if not ifile_fullpath:
            #this code path is used when the current BT node has no description.
            #it could be replaced by a dummy node, but I think it is wiser to
            #raise an exception as soon as possible, to warn the developper
            raise Exception('in BTManager.BT2xml(): missing info file for node %s' % \
                            (os.path.join(rootpath, name)))

        #get xml representation of the node
        begin, end = self.ifile2xml(ifile_fullpath, parent_dirname=name)
        begin = [(BTManager.xml_indent_unit * depth) + begin]

        #make sure there's no children here if we are a leaf node.
        _, ifile_name = os.path.split(ifile_fullpath)
        subdirs = self.get_subdirs(os.path.join(rootpath, name))
        if (ifile_name in Config.instance().BT_leaves_classes_names) and subdirs:
            raise Exception('in BTManager.BT2xml(): missing info file for node %s' % \
                            (os.path.join(rootpath, name)))

        #insert descriptions of child nodes
        for child_fullpath in subdirs:
            child_path, child_name = os.path.split(child_fullpath)
            begin.append((BTManager.xml_indent_unit * depth) + self.BT2xml(child_path, child_name, depth + 1))
        if end:
            begin.append((BTManager.xml_indent_unit * depth) + end)
        return '\n'.join(begin)

    def ifile2xml(self, ifile_fullpath, parent_dirname='unknown'):
        """
        Returns 2 xml strings  representating the content of the file pointed
        by the given fullpath.
        The first returned string is the opening <MyBTClass attr="value"> part.
        The second returned string is the closing <MyBTClass/> part.
        """
        #print 'ifile2xml() on ', ifile_fullpath
        ifile_path, ifile_name = os.path.split(ifile_fullpath)

        #once again, make sure the requested class exists
        if not ifile_name in (Config.instance().BT_nodes_classes_names + \
                              Config.instance().BT_leaves_classes_names):
            raise Exception('in BTManager.ifile(): unrecognised class \'%s\'' % ifile_name)

        xmlstring = ['<%s ' % ifile_name]
        if Config.instance().BT_add_debug_info_into_xml:
            xmlstring.append('__parentDirName="%s"' % parent_dirname)

        with open(ifile_fullpath) as file:
            for line in map(str.strip, file.readlines()):
                #slip empty line
                if not line:
                    continue
                #skip comments
                if line.startswith('#'):
                    continue
                if '=' in line:
                    split = line.split('=')
                    attr, value = split[0], split[1:]
                    value = '='.join(value)
                else:
                    #boolean
                    attr, value = line.strip(), '1'
                value=value.replace('<','&gt;').replace('>','&lt;')
                xmlstring.append(' %s="%s"' % (attr, value))

            if Config.instance().BT_add_debug_info_into_xml:
                xmlstring.append(' __source_file_repath="%s"' % \
                                 os.path.relpath(ifile_fullpath, self.src_path))
        #leaves are terminated as soon
        if ifile_name in list(Config.instance().BT_leaves_classes_names):
            xmlstring.append(' />')
            return ''.join(xmlstring), ''
        #nodes need some space in between
        xmlstring.append('>')
        return ''.join(xmlstring), '</%s>' % ifile_name

    def save_string_to(self, xmlstring, fullpath):
        """
        Write the given string at the given location.
        """
        print 'BTManager.save_string_to(%s)' % fullpath
        with open(fullpath, 'w') as f:
            f.write(xmlstring)

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
        Takes a path and returns the first file that fits info_files criteria:
            - its name is a BT class name
            - it does not start with __
        That's it.
        """
        #print 'get_ifile at', dir_fullpath
        for fullpath in glob.glob(os.path.join(dir_fullpath, '*')):
            #skip folders
            if not os.path.isfile(fullpath):
                continue
            path, name = os.path.split(fullpath)
            #skip info files that are not recognized, and warn about them
            if name not in (Config.instance().BT_nodes_classes_names + \
                            Config.instance().BT_leaves_classes_names):
                if Config.instance().BT_warn_for_unexpected_infofiles:
                    print 'WARNING: in BTManager.get_ifile(%s): ' \
                        'unrecognized BT class: %s. Not using this file.' \
                        % (dir_fullpath, name)
                continue
            return fullpath
        return None

if __name__ == '__main__':
    btman = BTManager()
    btman.export(src_path='/media/z2/python/1105/Weld/src/data/resources/BT',
                 dst_path='/media/z2/python/1105/weld_testing_folder/BT',
                 names=['BT_peaceful'])
