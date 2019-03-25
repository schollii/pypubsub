# this file gets copied to wx/lib/pubsub folder when release to wxPython

For wxPython users:

The code in wx/lib/pubsub folder was originally part of the wxPython source base, 
but was eventually moved into its own project, PyPubSub, first hosted on 
SourceForget.net and eventually (2016) moved to github. 
The code in wx/lib/pubsub is actually a snapshot taken from pypubsub on github,
included as part of the wxPython distribution for convenience to wxPython users,
but it may not be the latest, or the right version for you. It is highly 
recommended that you install pypubsub from pypi: 

- With Python 2.7, install pypubsub 3.4 from pypi: `pip install pypubsub=3.4`
- With Python 3+, install pypubsub 4+ from pypi: `pip install pypubsub`

Note that PyPubSub does not have any external dependencies and can be
used with PyQt, PyGTK, etc.

There is a wxPython example in PyPubSub source distribution /examples folder,
and wx/lib/pubsub/examples. The WxPython wiki also discusses usage of pubsub in
wxPython, the latest docs are only maintained at pypubsub.readthedocs.org

Although the wxPython wiki discusses usage of pubsub in wxPython, some of the code
there is outdated. Prefer the official pypubsub documentation, and the example
in the /examples/basic.

Oliver Schoenborn
March 2019

