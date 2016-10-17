Contribute
============

This page is intended mostly for developers. 

.. contents:: In this section:
   :depth: 1
   :local:


.. _label-roadmap:

Roadmap
--------

List of things I would like to add to pubsub:

- completed implementation of support for pubsub over UDP sockets, which
  would allow two pubsub-apps to publish and subscribe to messages of other
  applications (pseudo-code already in src/contrib)
- complete implementation of multi-threading helper class, no change
  required to pubsub, rather just utility class to help user
  (pseudo-code already in src/contrib)
- figure out a good way to prevent wrapped listener subscriptions from being DOA
  (pubsub only keeps weak reference to listener, so if listener subscribe like
  ``pub.subscribe( wrapper(yourListener) )`` then listener will be unsubscribed
  as soon as subscribe returns; you need
  ``refListener = wrapper(yourListener); pub.subscribe(refListener)``)
- finish the src/contrib/monitor implementation to monitor pubsub messages,
  or some way of monitoring message sending

If anyone is interested in helping, please contact me.

.. _label-contributing:

Contributing
-------------

Contributions are welcome! There are many ways you could contribute:

- bug fixes
- new features
- test results on different platforms
- documentation
- screencasts! (of applications using pubsub with output when user clicks)
- example topic trees (using ``pubsubutils.printTopicTree()`` in latest
  version, or ``print Publisher`` in versions 1)
- other improvements
- money!

Please contact me via email (schoenborno, at
users.sf.net) or by posting on the forums (links in the
:ref:`label-support` section).


System Requirements
---------------------

In addition to the :ref:`label-install-reqs`, the following are required:

- To run unit tests:

  - nose >= 0.10
  - coverage >= 3.1b1


- To generate these docs:

  - sphinx >= 0.6.3; note that sphinx must be patched as per post on
    sphinx-dev:

    .. literalinclude:: sphinx_patch1.txt
    .. literalinclude:: sphinx_patch2.txt



Scripts Available
------------------

The following is likely to be useful to pubsub developers and contributors only.

*Testing*:
    The package currently gets tested on Windows XP only. The tests can be
    run automatically by running :command:`runtests.bat` from the :file:`tests`
    folder of a source distribution.

    If anyone is able to run the test suite on other platforms, please let
    me know of the results. A Linux person will have no
    trouble running the equivalent batch commands on Linux.

*Documentation*:
    The documentation can be generated on Windows by running
    :command:`gendocs.bat` from the :file:`docs` folder of a source
    distribution (but see the note about Sphinx patch in next section).
    For Linux, again you should be able to
    just copy the commands form the :file:`.bat` file to a shell window.

*Performance*:
    A small performance test is available in the :file:`tests` folder.
    On Windows, run it via :command:`runperf.bat`. On Linux, you'll have
    to convert the file to a bash script (the .bat file is very simple,
    no branching etc), or run the commands manually.


Packaging
------------

PyPubSub requires setuptools to be packaged for distribution. 

For packaging py2exe or cx_Freeze, there is a separate section:

.. toctree::

   py2exe.rst
   
For packaging into .deb package, there is a separate section:

.. toctree::

   deb.rst
