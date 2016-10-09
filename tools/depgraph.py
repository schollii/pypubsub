'''
This script generates a dependency graph as a PNG file. 
It uses the depgraph2dot and py2depgraph scripts from 
http://www.tarind.com/depgraph.html and calls graphviz's
dot command (http://www.research.att.com/sw/tools/graphviz/)
to generate the PNG file. 

Some parameters can be changed, all in one section of code below 
class MyDepGraphDot. Note that the 'exclude' list excludes 
modules from the analysis: this means anything imported by 
those modules gets ignored too. 

Oliver Schoenborn
Nov 2007
'''

import sys, os
from tempfile import mkstemp
from getopt import getopt, GetoptError
from subprocess import call as oscall
from depgraph2dot import pydepgraphdot
from py2depgraph import mymf

from pubsub import pub

def genDepGraph(inScript, options):
    path = sys.path[:]
    debug = 0
    mf = mymf(path, debug, options.exclude)
    mf.run_script(inScript)
    
    # find all modules in standard lib and set them aside for later;
    # assume that modules that don't have a filename are from stdlib
    ignore = set()
    for moduleName, module in mf.modules.iteritems():
        ign = False
        if options.ignoreNoFile and (not module.__file__):
            ign = True
        if options.ignoreStdlib and module.__file__:
            path1 = os.path.abspath(os.path.dirname(module.__file__)).lower()
            path2 = os.path.abspath('c:\python24\lib').lower()
            if path1 == path2:
                ign = True
        if ign:
            ignore.add(moduleName)
            
    return dict(depgraph=mf._depgraph, types=mf._types), ignore


class MyDepGraphDot(pydepgraphdot):
    def __init__(self, buffer, ignore=None):
        self.__depgraph = buffer['depgraph']
        self.__types = buffer['types']
        tmpfd, tmpname = mkstemp('.dot', 'depgraph_')
        os.close(tmpfd)
        self.__output = file(tmpname, 'w')
        self.__output_name = tmpname
        self.__ignore = ignore or set()
        #print 'Will ignore modules:', self.__ignore
        
    def toocommon(self, s, type):
        if s in self.__ignore:
            return 1
        return pydepgraphdot.toocommon(self, s, type)
    
    def get_data(self):
        return self.__depgraph, self.__types
    def get_output_file(self):
        return self.__output
    def get_output_name(self):
        self.__output.close()
        return self.__output_name


class Options:
    def __init__(self):
        self.exclude = []        # list of module names to exclude from analysis
        self.ignoreStdlib = True # modules from Python's stdlib will not be in graph
        self.ignoreNoFile = True # modules that don't have an associated file will not be in graph
        self.dotPath = r'C:\Program Files\Graphviz2.16\bin\dot'
        self.args = []

        try:
            options, args = getopt(sys.argv[1:], 'hsfe:d:', ['--help'])
            self.args = args
        except GetoptError, exc:
            print 'ERROR:', exc
            self.usage()
            sys.exit(-1)
            
        for o,v in options:
            if o=='-s':   self.ignoreStdlib = False
            elif o=='-f': self.ignoreNoFile = False
            elif o=='-e':
                self.exclude = v.split(',')
            elif o=='-d':
                self.dotPath = v
            else: # also covers -h cases
                self.usage()
                sys.exit()
                
        if len(args) > 1:  #includes path to script
            print 'ERROR: Can only generate graph for one file, remove', ','.join(args[1:])
            self.usage()
            sys.exit(-1)
        elif not args:
            print 'ERROR: Must specify for which file to generate dependencies graph'
            self.usage()
            sys.exit(-1)
            
        print 'Will %sinclude stdlib modules' % (self.ignoreStdlib and 'NOT ' or '')
        print 'Will %sinclude "file-less" modules' % (self.ignoreNoFile and 'NOT ' or '')
        print 'Will exclude the following modules and anything imported by them:', self.exclude
        print 'Will use "%s" as dot' % self.dotPath

    def usage(self):
        print 'Usage:\n%s [-s] [-f] [-e list] [-d dotPath] file.py' % sys.argv[0]
    

# Process command line args
options = Options()

# start processing script for dependencies
inScript = options.args[0]
try:
    buffer, ignore = genDepGraph(inScript, options)
except IOError, exc: 
    print 'ERROR:', exc
    sys.exit(-1)
    
if not buffer['depgraph']:
    print 'NO dependencies of interest! Nothing to generate, exiting.'
    sys.exit()
    
dotdep = MyDepGraphDot(buffer, ignore)
dotdep.main( sys.argv )

# convert to png
basename = os.path.splitext(os.path.basename(inScript))[0]
pngOutput = basename + '_depgraph.png'
print 'Generating %s from %s' % (pngOutput, dotdep.get_output_name())
oscall([
    options.dotPath, '-Tpng', '-o', pngOutput, dotdep.get_output_name()]
    )

# cleanup
os.remove(dotdep.get_output_name())
