import os.path
import sys

import cPickle as pickle
import os
from debug import curr_f

class Savable(object):
    """
    Subclasses can register variable name to be saved when "save" is classed.
    They can also load from file they have created.
    """
    def __init__(self, savepath):
        """
        savepath: directory where the file is saved.
        """
        self.savepath = savepath
        self.savelist = []

    def add_to_savelist(self, varname):
        """
        adds a variable name to the list of those which will be pickled.
        """
        self.savelist += [varname]

    def load(self):
        if os.path.exists(self.savepath):
            file = open(self.savepath)
            unpickled = pickle.load(file)
            file.close()
            loaded = []
            for k, v in unpickled.iteritems():
                setattr(self, k, unpickled[k])
            diff = set(self.savelist)-set(unpickled.keys())
            if diff:
                s = 'Some attributes that would have been saved were\'nt '\
                'found in the loaded file:\n%s' % ', '.join(diff)
                print >> sys.err, curr_f(), s

    def save(self):
        """
        Saves the object into <self.savepath>.
        """
        toPickle = {}
        for varname in self.savelist:
            if hasattr(self, varname):
                toPickle[varname] = getattr(self, varname)
            else:
                s = 'Trying to save a var that does not exist: \'%s\'' % varname
                print >> sys.err, curr_f(), s

        filepath, filename = os.path.split(self.savepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        try:
            # backup previous save
            if os.path.exists(self.savepath):
                os.rename(self.savepath, self.savepath + '.back')

            # create dir if necessary
            dirpath, _ = os.path.split(self.savepath)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, 'rwx')
                
            # do actual saving
            file = open(self.savepath, 'wb')
            pickle.dump(toPickle, file)
            file.close()

            # remove backup
            if os.path.exists(self.savepath + '.back'):
                os.remove(self.savepath + '.back')
        except Exception, e:
            raise
            print >> sys.stderr, 'in Savable%s.save():' % self, e.args


