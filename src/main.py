#!/usr/bin/python

__author__ = "onze"
__date__ = "$7-May-2011 4:24:35 PM$"

print 'bootstrapping...'

import sys
import os

root,script=os.path.split(os.path.abspath(__file__))
plugins_path=os.path.join(root,'plugins')

#making sure we are where we should
os.chdir(root)

#making sure we can load shared object modules located in the plugins folder
if 'LD_LIBRARY_PATH' not in os.environ or plugins_path not in os.environ['LD_LIBRARY_PATH']:
    print 'adding weld\'s root folder to LD_LIBRARY_PATH and relaunching...'
    if 'LD_LIBRARY_PATH' not in os.environ:
        os.environ['LD_LIBRARY_PATH']=''
    os.environ['LD_LIBRARY_PATH']=':'.join([plugins_path,os.environ['LD_LIBRARY_PATH']])
    os.execve(script, (script,), os.environ)
else:
    print 'LD_LIBRARY_PATH:',os.environ['LD_LIBRARY_PATH']

from weld import Weld

weld = Weld()
weld.run()
