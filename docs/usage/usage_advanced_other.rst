
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

Pubsub supports two ways to send messages and transmit the data to listeners: 

- kwargs: this is the syntax that requires each message datum to be a separate
  keyword argument in the sendMessage, i.e. ``pub.sendMessage(topicName, **msgArgs)``. 
  The listener signature can provide default values to its arguments, in which 
  case the corresponding message data are optional: 
  ``def listener(a, b, c=1, d=2): pass`` is a listener that requires a and b, and 
  optonally accepts c and d. 
- arg1: this is the syntax that requires all message data to be inserted in one 
  object, i.e. ``pub.sendMessage(topicName, msg)`` and  ``pub.sendMessage(topicName, msg)``.
  I.e. msg is optional. The listener must access fields of msg to retrieve the 
  message data. 

The arg1 was the first and only protocol of pubsub. It was difficult to 
specify what data was allowed in a topic, thus requiring the developer to put in 
verification code in the listener, having to deal with exceptions resulting 
from mismatches in field names, etc, it worked but for larger applications it
involved more effort than seemed necessary. 

The kwargs protocol was then designed: it allows the sender to name each datum, 
and the recipient (listener) to be checked via introspection at subscription time
for its capability to receive the data. It also made it easier to document the 
message data. The protocol was implemented as pubsub version 3.

Due to the significant differences between the two, and the goal of kwargs being
to allow for better runtime checks by pubsub, only one protocol can be active 
when importing pubsub: the application must choose either kwargs or arg1. 
The default is the kwargs protocol. In order to use arg1, the application must 
import pubsub.setuparg1. 

The only reason for using the arg1 protocol is to avoid upgrading an
application that was developed when this protocol was the only choice. Any 
new application should use the default kwargs protocol. 


.. _label-pubsub_versions:

API Versions
---------------------------

As pubsub matured, its API went through 2 dramatic changes: 

- API version 1 (v1): the version that was part of wxPython.
- API version 2 (v2): also part of wxPython, made various improvements but was short 
  lived as it did not properly address some inherent limitations of version 1.
- API version 3 (v3): pubsub was moved out of wxPython to be a standalone project. Since
  then, wxPython's wx.lib.pubsub is a verbatim copy of the standalone pubsub. This API 
  supports 2 messaging protocols: arg1 and kwargs. The arg1 protocol is supported only 
  as required for backwards compatibility. 

The API version is different from the PyPubSub release version: 

* API v1 was given secondary status as of pypubsub v3.0. It was supported until 
  the end of pypubsub v3.1.x by importing pubsub.setupv1, but deprecated. 
  Starting from pypubsub version 3.2, the v1 API (and hence pubsub.setupv1) 
  was no longer available as part of pubsub. 

  The version 1 API was the default in wx.lib.pubsub until pubsub version 3.1.0 
  (wx.lib.pubsub did the setupv1 import automatically). After that, it was 
  deprecated. Eventually the default in wx.lib.pubsub was the v3 API with kwargs 
  protocol; users had to manually import setuparg1 once in their application if they 
  did not want to port their application to use the kwargs protocol. If this was a 
  problem, they could continue to use setupv1. WxPython Phoenix will use pubsub 3.3,
  with the default being the kwargs protocol, and no support for v1 API. 
  
* API v3: Starting with pypubsub version 3.3, the arg1 messaging protocol is 
  officially deprecated. It was finally removed in pypubsub 3.4.0.

  
Receiving all data of a topic
------------------------------

Listener uses \**kwargs then will be given all data of message,
not just portion specific to registration topic. For example, ::

    >>> def listener(**kwargs): pass
    >>> pub.subscribe(listener, 'topic')
    >>> pub.sendMessage('topic', arg1=1, arg2=2)

Then listener will receive arg1 and arg2. 
