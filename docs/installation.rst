Install
===============

.. contents:: In this section:
   :depth: 1
   :local:

.. _label-install-reqs:

System Requirements
--------------------

Requires Python 2.6 to 2.7. DO NOT USE WITH PYTHON 3+. For Python 3+, use pypubsub 4+.

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

Please post on pypubsub forum (see :ref:`label-support` section) if you have 
successfully used pubsub with other combinations of Python and Platform.

Many thanks to Jerome Laheurte for providing a buildbot with Linux and OSX VM's 
for continuous testing. 

How-to
--------------

Several methods are available: egg distribution, Windows installer, zip file with source, or
directly from source code repository.

Method 1. Using pip
^^^^^^^^^^^^^^^^^^^^^

With pip installed on your system, do :command:`pip install pypubsub`.

If you want the developer version, you can try :command:`pip install --pre pypubsub`.


Method 2. Using setuptools (easy_install)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

With setuptools installed on your machine, do :command:`easy_install -Z pypubsub` in a console/shell window.

If for whatever reason easy_install can't find the pypubsub download, you could try manually
downloading the `egg distribution
<http://sourceforge.net/projects/pubsub/files/pubsub/>`_
from SourceForge.net. Then do :command:`easy_install -Z <downloaded_egg>`


Method 3. Using Installer (Windows only)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Download the `Installer (PyPubSub-xxx.win32.exe)
<http://sourceforge.net/projects/pubsub/files/pubsub/>`_
from SourceForge.net and run it.

Method 4. From source distribution
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Download the appropriate `ZIP file
   <http://sourceforge.net/projects/pubsub/files/pubsub/>`_
   from SourceForge.net.
2. Extract the contents
3. From a console window, cd'd to extracted folder, do :command:`python setup.py install`


Method 5. From source code repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1. Using a subversion client, do an SVN checkout of
   **svn://svn.code.sf.net/p/pubsub/code/trunk** or
   **http://svn.code.sf.net/p/pubsub/code/trunk**
2. From a console window, cd to working copy
3. In console, do :command:`python setup.py install`

.. image:: http://sflogo.sourceforge.net/sflogo.php?group_id=197063&amp;type=2
   :alt: SourceForge.net Logo
   :width: 125
   :height: 37
   :target: http://sourceforge.net


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
