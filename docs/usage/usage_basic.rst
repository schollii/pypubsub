
.. _label-usage-basic:

Basic Usage
===========

Basic usage of PyPubSub involves subscribing listeners, sending messages, and responding to
messages. The :ref:`label-quick-start` subsection below provides examples. For details, 
navigate to the :ref:`label-basic-tasks` subsection: 

.. toctree::
   :maxdepth: 2
   
   usage_basic_tasks
   
.. _label-quick-start:

Quick Start
-----------

Simplest example of use:

.. literalinclude:: helloworld.py


Running the above as a script (available in the docs/usage folder of the source 
distribution as helloworld.py) will produce the result::

    Publish something via pubsub
    Function listener1 received:
      arg1 = 123
      arg2 = {'a': 456, 'b': 'abc'}

      
Other Examples 
^^^^^^^^^^^^^^

There are several examples that can be found in the source distribution
in the ``examples`` folder. Some focus on the basics, others on more 
advanced aspects of PyPubSub usage. Some examples are GUI-based and may
require other packages (such as wxPython).

The examples/basic_kwargs folder contains examples of basic usage of PyPubSub
"out of the box", i.e. using the default ("kwargs") messaging protocol. 
The README.txt file in `examples_basic_kwargs`_ explains:

.. include:: ../../examples/basic_kwargs/README.txt


.. _examples_basic_kwargs: http://svn.code.sf.net/p/pubsub/code/trunk/examples/basic_kwargs


