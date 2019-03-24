
Other
=====

.. contents:: In this section:
   :depth: 2
   :local:


Dev app (process)
-----------------

Suggestions while developing application that uses PyPubSub:

- Design your application into independent modules or subpackages 
  that don't import one another
- Define basic topics exist in the application: 'user' (events from 
  user interface), 'filesystem' (events from local filesystem), etc. 
  These are your messaging topics. You may find it useful
  to use ``printTreeDocs`` from ``pubsub.utils``. 
- Use Topic Definition Providers as eary as possible. Use
  pub.exportTopicTreeSpec() if already have partial implementation, 
  and pub.addTopicDefnProvider() and pub.setTopicUnspecifiedFatal().
- Start all listener functions and methods with *pubOn*, for 
  instance ``def psOnCloseDocument()``
- Define some data for each message type, and which data are optional/required
- Implement your modules

    - Subscribe listeners with appropriate signature (according to 
      data for each topic/event type)
    - Send messages with appropriate data
    - Handle messages in listeners, without making any assumptions 
      about sender or order of receipt
    
- Testing: import your control modules and generate messages to exercise them.

You can see a very informative view of an application before and after 
incorporatng PyPubSub, at `Steven Sproat's dev site`_ (click "expand all"
and "show diffs side-by-side"). Steven says: 
  
  *You can see how I removed some GUI logic from the Canvas class (a 
  child of the GUI) and placed "controller" functions into my GUI that 
  subscribed to PyPubSub topics and delegates to the appropriate classes.*

.. _Steven Sproat's dev site: http://bazaar.launchpad.net/~sproaty/whyteboard/development/revision/286 


.. _label-msg_protocols:

Messaging Protocol
------------------

The very first version of PyPubSub supported a messaging protocol that became
known as 'arg1'. This protocol made it difficult to specify (i.e. define) what
data was allowed in a topic. For larger applications, the developer had to put in
verification code in the listener, had to deal with exceptions resulting
from mismatches in field names in the message object, etc. It worked but
made debugging the use of topics and PyPubSub messages complicated.

The kwargs protocol was then designed: it allows the sender to name each datum, 
and the recipient (listener) to be checked via introspection at subscription time
for its capability to receive the data. It also makes it easier to document the
message data, and to specify it. The protocol was implemented in PyPubSub version 3.

PyPubSub v4 supports only one way of transmitting data to listeners, namely via the
'kwargs' protocol. Since this is the only protocol supported, there is no code left
that handles protocol name or selection.


.. _label-pubsub_versions:

API Versions
------------

As PyPubSub matured, its API went through changes:

- API version 1 (PyPubSub v1): the version that was part of wxPython and supported only the arg1 protocol.
- API version 2 (PyPubSub v2): also part of wxPython, it made various improvements on v1 but was short
  lived as it did not properly address some inherent limitations of version 1.
- API version 3 (PyPubSub v3): PyPubSub was moved out of wxPython to be a standalone project and
  supported 2 messaging protocols: the original arg1 for backwards compatibility, and the new
  kwargs. Since then, wxPython's wx.lib.pubsub is a verbatim copy of the standalone PyPubSub. The
  arg1 protocol was deprecated.
- API version 4 (PyPubSub v4): Support for arg1 was dropped; only kwargs is now supported, which
  simplifies the code base considerably.

  
Receiving all data of a message
-------------------------------

If a Listener uses \**kwargs then it will be given all data of a message,
not just the portion specific to the topic it is subscribed to. For example, ::

    >>> def listener0(arg1, arg2): print('listener0: ', arg1, arg2)
    >>> def listener1(**kwargs): print('listener1: ', kwargs)
    >>> pub.subscribe(listener0, 'topic')
    >>> pub.subscribe(listener1, 'topic')
    >>> pub.sendMessage('topic', arg1=1, arg2=2)

Then listener1 will receive arg1 and arg2.

Note: as explained in :ref:`label-topic_tree_def`, PyPubSub infers a topic's *Message Data Specification*
based on the first listener subscribed, unless there is a *Topic Definition Provider* for the topic. In the above
example, PyPubSub would infer that *topic* has 2 required data: arg1 and arg2. However, if listener1
were subscribed first, PyPubSub would infer that *topic* had no required data (because there are
no positional parameters in the listener1 signature), and no optional data (because there are no
parameters with default values in the the listener1 signature). Thus the subscription of listener0
to *topic* would raise an exception (because listener0 requires arg1 and arg2). In real-world code,
it can be difficult
to guarantee the order of registration of listeners. Such issue is one of the intended use cases
for a *Topic Definition Provider*, as explained in :ref:`label-topic_tree_def`.
