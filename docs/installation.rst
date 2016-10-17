Install
===============

.. contents:: In this section:
   :depth: 1
   :local:

.. _label-install-reqs:

System Requirements
--------------------

Requires either Python >= 3.3 or pypy3. It has been tested on Windows 7 and various
flavors of \*nix (such as Fedora, OpenSuse, Ubuntu and OSX). For Python < 3.5, there are
additional requirements:

- Python 3.4: requires the "typing" package (from PyPI)
- Python 3.3: 3.4 requirements + enum34, pathlib and weakrefmethod (all on PyPI)
- Pypy3 2.4 (which is technically Python 3.2): 3.3 requirements + importlib (from PyPI)
- Python 3.2 (not tested, but based on pypubsub working with pypy3 2.4): same as pypy3 requirements

Please post on pypubsub forum (see :ref:`label-support` section) if you have 
successfully used pubsub with other combinations of Python and Platform.

Many thanks to Jerome Laheurte for providing a buildbot with Linux and OSX VM's 
for continuous testing. 

How-to
--------------

With pip installed on your system, do :command:`pip install pypubsub`.

If you want the developer version, you can try :command:`pip install --pre pypubsub`.


.. _label-support:

Support
--------

The forums are currently hosted on google groups:

- http://googlegroups.com/group/pypubsub: PyPubSub general help and support (hosted by Google Groups)

- http://googlegroups.com/group/pypubsub_dev: PyPubSub bug reports, feature suggestions, patches, etc (hosted by Google Groups)

Also, many pypubsub users are on the `wxPython-users mailing list  <http://www.wxpython.org/maillist.php>`_.


Release Notes
---------------

.. include:: ../src/pubsub/RELEASE_NOTES.txt


.. include:: changelog.rst
