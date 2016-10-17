# this file gets copied to wx/lib/pubsub folder when release to wxPython

For wxPython users who are using wx.lib.pubsub:

Pubsub originated as a wxPython lib, but it is now a standalone project
on github (previously on SourceForge). The code in wx/lib/pubsub folder
is taken verbatim from the standalone PyPubSub project (each version of
wxPython includes a different version of pypubsub) for convenience to
wxPython users. Pypubsub does not have any external dependencies; it can be
used with PyQt, PyGTK, etc. The version included with wxPython can be
replaced with a compatible version of pypubsub, and in some cases
(depending on your use of pubsub) by the latest version.

There is a wxPython example in wx/lib/pubsub/examples. The WxPython
wiki also discusses usage of pubsub in wxPython.

Oliver Schoenborn
October 2016
