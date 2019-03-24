Install
===============

.. contents:: In this section:
   :depth: 1
   :local:

.. _label-install-reqs:

System Requirements
--------------------

Requires Python 2.7. DO NOT USE WITH PYTHON 3+. For Python 3+, use PyPubSub 4+.

The following table identifies on which
combination of Python and Platform the unit tests have been run. The result
for each combination is number of tests passed out of total number of tests,
or "n/t" for "not tested":

    ============ =========== =========== =============
         \        Windows 7   Linux(++)     OSX
    ============ =========== =========== =============
    Python 2.7    64/64        64/64       64/64
    ============ =========== =========== =============

    Notes:
    (++) Tested on Fedora, OpenSuse, and Ubuntu.

Please post on PyPubSub forum (see :ref:`label-support` section) if you have 
successfully used pubsub with other combinations of Python and Platform.

Many thanks to Jerome Laheurte for providing a buildbot with Linux and OSX VM's 
for continuous testing. 

How-to
------

Several methods are available.

Method 1. Using pip
^^^^^^^^^^^^^^^^^^^

With pip installed on your system, do :command:`pip install pypubsub==3.4` (if you have 
both Python 2 and 3 on your system, you may have to specify pip2 instead of pip).


Method 2. From source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Download the appropriate zip file from https://github.com/schollii/pypubsub/releases
2. Extract the contents
3. From a console window, cd to extracted folder, then do :command:`python setup.py install`


Method 3. From source code repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Browse to https://github.com/schollii/pypubsub/tree/v3.4.0
2. Click on the "Clone or Download" button, then "Download zip"
3. Extract the contents
4. From a console window, cd to extracted folder, then do :command:`python setup.py install`


.. _label-support:

Support
--------

- use tag ``pypubsub`` on stackoverflow.com
- post on pypubsub's Gitter channel: https://gitter.im/pypubsub/community
- post bug reports, feature suggestions, pull requests: https://github.com/schollii/pypubsub
- older but still used google group: http://googlegroups.com/group/pypubsub

Also, many PyPubSub users are on the `wxPython-users mailing list  <http://www.wxpython.org/maillist.php>`_.


Release Notes
---------------

.. include:: ../src/pubsub/RELEASE_NOTES.txt


.. include:: changelog.rst
