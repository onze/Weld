import os.path
import sys
import cPickle as pickle

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
            for k, v in unpickled.items():
                setattr(self, k, unpickled[k])

    def save(self):
        """
        Saves the object under the given filename.
        One can omit the filename if one has already called the load method.
        The same filename is then used, and the file overwritten.
        """
        toPickle = {}
        for varname in self.savelist:
            if not hasattr(self, varname):
                raise Exception('Trying to save a var that does not exist: \'%s\'' % varname)
            toPickle[varname] = getattr(self, varname)

        filepath, filename = os.path.split(self.savepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        try:
            file = open(self.savepath, 'wb')
            pickle.dump(toPickle, file)
            file.close()
        except Exception, e:
            raise
            print >> sys.stderr, 'in Savable%s.save():'%self, e.args


