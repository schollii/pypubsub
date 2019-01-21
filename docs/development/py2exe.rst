Packaging with py2exe and cxFreeze
==================================

In this section we will see how to package applications that use
PyPubSub, with `py2exe`_ and `cx_Freeze`_ packaging tools.

Introduction
------------

Packaging tools such as py2exe and cx_Freeze determine the dependencies 
that have to be included in a package by recursively finding the modules
from the import statements used. Recursive finding of modules from the
import statements uses straight forward approach i.e., if the python
code dynamically imports certain modules by modifying the ``sys.path`` at
runtime or if the code uses ``__import__`` statements, those modules
are likely to be left out by the packaging tool. This can be a problem
for some packaged applications.


Packaging modules that use PyPubSub
-----------------------------------

PyPubSub supports two different messaging protocols namely ``args1`` and
``kwargs``; choosing and switching between these protocols is done by
modifying the module path dynamically. This can result in import error
like this at runtime::

      from listenerimpl import Listener, ListenerValidator
      ImportError: No module named listenerimpl

In the following sections we show an example script that uses
PyPubSub and discuss the setup script to package it using *py2exe* or
*cx_Freeze* packaging tools.

.. _py2exe: http://www.py2exe.org
.. _cx_Freeze: http://cx-freeze.sourceforge.net

Example
-------

Consider a sample application which has a single file named say
``testpubsub.py``

.. literalinclude:: testpubsub.py

To package this with *py2exe* and *cx_Freeze* you
write a conventional ``setup.py`` module, but with extra options that 
the packaging tool uses to create the final distribution. 

Setup file using py2exe
-----------------------

The ``setup.py`` for this would look something like this

.. literalinclude:: setup-py2exe.py

The line ``'packages': 'encodings, pubsub'`` explicitly
tells *py2exe* to include ``pubsub`` as a package so that the entire pubsub
folder (from the installation location) including its sub packages are
included for packaging. As the package has the entire list of python
modules under pubsub, runtime protocol selection is now possible in
the generated ``exe`` file.

To build, run::

   python setup.py py2exe

which will produce a dist folder containing ``testpubsub.exe`` and other 
DLLs and files required to run the application. Interestingly, py2exe 
command complains about modules that *appear* to be missing: 

  The following modules appear to be missing
  ['callables', 'core', 'core.notificationmgr', ... , 'topicu', 'validatedefnargs']
  
however, the application runs fine. 

Setup file using cx_Freeze
--------------------------

The ``setup.py`` for this would look something like this

.. literalinclude:: setup-cxfreeze.py

To build, run::

   python setup.py build

We can safely ignore the missing modules warning in the build log::

   Missing modules:
   ? core.publisher imported from pubsub.pub
   ? listenerimpl imported from pubsub.core.listener
   ? publishermixin imported from pubsub.core.topicobj
   ? topicargspecimpl imported from pubsub.core.topicargspec
   ? topicmgrimpl imported from pubsub.core.topicmgr


