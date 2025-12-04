# this file gets copied to wx/lib/pubsub folder when release to wxPython

For wxPython users who are using wx.lib.pubsub:

Do not use wx.lib.pubsub: this package is an earlier version of PyPubSub that
was copied into wxPython for legacy reasons. If you attempt to use wx.lib.pubsub
in wxPython >= 4.0.4, you will get a deprecation message that you should install
pubsub directly from PyPubSub.

Note that PyPubSub does not have any external dependencies and can be
used with PyQt, PyGTK, etc.

There is a wxPython example in PyPubSub source distribution /examples folder,
and wx/lib/pubsub/examples. The WxPython wiki also discusses usage of pubsub in
wxPython, the latest docs are only maintained at pypubsub.readthedocs.org

