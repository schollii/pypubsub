
Other
========

.. contents:: In this section:
   :depth: 2
   :local:


Dev app (process)
------------------

Suggestions while developing application that uses pubsub:

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
incorporatng pubsub, at `Steven Sproat's dev site`_ (click "expand all" 
and "show diffs side-by-side"). Steven says: 
  
  *You can see how I removed some GUI logic from the Canvas class (a 
  child of the GUI) and placed "controller" functions into my GUI that 
  subscribed to pubsub topics and delegates to the appropriate classes.*

.. _Steven Sproat's dev site: http://bazaar.launchpad.net/~sproaty/whyteboard/development/revision/286 


.. _label-msg_protocols:

Messaging Protocol
---------------------

The very first version of PyPubSub supported a messaging protocol that became
known as 'arg1'. This protocol made it difficult to specify (i.e. define) what
data was allowed in a topic. For larger applications, the developer had to put in
verification code in the listener, had to deal with exceptions resulting
from mismatches in field names in the message object, etc. It worked but
made debugging the use of topics and pubsub messages complicated.

The kwargs protocol was then designed: it allows the sender to name each datum, 
and the recipient (listener) to be checked via introspection at subscription time
for its capability to receive the data. It also makes it easier to document the
message data, and to specify it. The protocol was implemented in pubsub version 3.

Pubsub v4 supports only one way of transmitting data to listeners, namely via the
'kwargs' protocol.


.. _label-pubsub_versions:

API Versions
---------------------------

As pubsub matured, its API went through changes:

- API version 1 (pubsub v1): the version that was part of wxPython and supported only the arg1 protocol.
- API version 2 (pubsub v2): also part of wxPython, it made various improvements on v1 but was short
  lived as it did not properly address some inherent limitations of version 1.
- API version 3 (pubsub v3): pubsub was moved out of wxPython to be a standalone project and
  supported 2 messaging protocols: the original arg1 for backwards compatibility, and the new
  kwargs. Since then, wxPython's wx.lib.pubsub is a verbatim copy of the standalone pubsub. The
  arg1 protocol was deprecated.
- API version 4 (pubsub v4): Support for arg1 was dropped; only kwargs is now supported, which
  simplifies the code base considerably.

  
Receiving all data of a topic
------------------------------

Listener uses \**kwargs then will be given all data of message,
not just the portion specific to registration topic. For example, ::

    >>> def listener(**kwargs): pass
    >>> pub.subscribe(listener, 'topic')
    >>> pub.sendMessage('topic', arg1=1, arg2=2)

Then listener will receive arg1 and arg2. 
