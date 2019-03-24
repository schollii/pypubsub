Types of Errors
---------------

While developing an application that uses PyPubSub, calls to PyPubSub
functions and methods may raise an exception, in the following 
circumstances: 

* the listener given to pub.subscribe() is not valid: 
  
    - :py:class:`pub.ListenerMismatchError`
    - ``ValueError``
    
* the data sent via pub.sendMessage() does not satisfy the topic's MDS: 

    - :py:class:`pub.SenderMissingReqdMsgDataError`
    - :py:class:`pub.SenderUnknownMsgDataError`
    - :py:class:`pub.SenderTooManyKwargs`
    - :py:class:`pub.SenderWrongKwargName`
    
* there is a problem with a topic name: 

    - :py:class:`pub.TopicNameError`
    - :py:class:`pub.TopicDefnError`
    - ``ValueError``
    
* a callback registered via pub.setListenerExcHandler() raises an exception 
  while handling an exception raised by a listener:
  
    - :py:class:`pub.ExcHandlerError`
    
* a subclass derived from a pubsub core or utils base class is missing
  some implementation:
  
    - ``NotImplementedError``
  
* a topic's MDS, defined explicitly via TopicDefnProvider, is not valid: 
  
    - :py:class:`pub.MessageDataSpecError`
    - :py:class:`pub.UnrecognizedSourceFormatError`
    
For basic PyPubSub usage, the most common ones are ``ListenerMismatchError``
and the ``Sender...`` exceptions. All others are relevant to usage of
more advanced PyPubSub features such as topic tree specification,
listener exception trapping, and PyPubSub notification trapping.


Listener Mismatch Errors
^^^^^^^^^^^^^^^^^^^^^^^^

The most common type of error results from attempting to subscribe an invalid 
listener: one that does not have a signature (call protocol) compatible with the 
topic's MDS. When this happens, PyPubSub raises a
:py:class:`pub.ListenerMismatchError` exception. 

By default, PyPubSub infers topic MDSs. In that case, the error typically happens
when more than one listener is registered for a given topic, and introspection of 
the listener identifies that it does not satisfy the topic's MDS. For example, 
consider :: 

    def listener0(arg1, arg2=default0): pass
    def listener1(arg1=val, arg2=default3): pass
    def listener2(arg1): pass
    def listener3(arg1, arg2): pass
    
    pub.subscribe(listener0, "topic") // OK: infers MDS
    pub.subscribe(listener1, "topic") // OK: satisfies MDS
    pub.subscribe(listener2, "topic") // FAIL: violates MDS
    
PyPubSub will raise a ListenerMismatchError exception on the last line since arg2 was
inferred in the first subscription, from listener0, as being part of the MDS, yet 
listener2 does not accept this data. 

Similarly, if the last line had been ::

    pub.subscribe(listener3, "topic")
    
a ``pub.ListenerMismatchError`` exception would get raised because listener3 
*requires* arg2, 
yet the MDS inferred from listener0 has it as optional, indicating the sender
may not provide it. PyPubSub is flagging the fact that listener3 is "more demanding"
than the MDS can guarantee.

Sender Exceptions
^^^^^^^^^^^^^^^^^

The sender exceptions are very useful as they indicate clearly what message 
data is wrong: 

    - :py:class:`pub.SenderMissingReqdMsgDataError`: some required data is missing
    - :py:class:`pub.SenderUnknownMsgDataError`: one of the keyword arguments is 
      not part of MDS

For example, given the previous code involving a topic "topic" MDS inferred
from listener0, the following code would raise a 
``pub.SenderUnknownMsgDataError`` ::

    pub.sendMessage("topic", arg1=1, arg3=3) 

because arg3 is not part of the MDS. 


Topic Name Errors
^^^^^^^^^^^^^^^^^

A topic name must satisfy the following: 

- is not empty: '' or None
- is not a reserved name: the only one currently is the value of :py:data:`pub.ALL_TOPICS`
- starts with any of '-', 0-9, a-z, A-Z (so UNDERSCORE '_' not allowed; it is reserved)

This applies to all levels of a topic path, i.e. the items between '.'. For example 
the following are not allowed: 'a.', '.a', '.', 'a..b', etc.

If a topic name does not satisfy the above, PyPubSub raises ``pub.TopicNameError``.

Some functions in PyPubSub raise an exception if the topic doesn't exist:

- :py:func:`pub.isValid(listener, topicName)`
- :py:func:`pub.validate(listener, topicName)`
- :py:func:`pub.isSubscribed(listener, topicName)`
- :py:func:`pub.unsubscribe(listener, topicName)`
- :py:func:`pub.unsubAll(topicName)`

since the operation does not make sense: it does not make sense, for example, 
to test if given listener is valid if topic does not exist!

By default, 

- PyPubSub does *not* complain about topic names that have never
  been subscribed to. 
- subscribing a listener to a topic never used before 'creates'
  the topic. 

Hence there is, by default, no way of trapping 
the following mistakes::

    pub.subscribe(listener1, 'topic')  # creates 'topic' topic
    # next line has typo in topic name:
    pub.subscribe(listener2, 'tpic')   # creates 'tpic' topic
    pub.sendMessage('topic') # only listener1 will receive
    # next line has typo in topic name:
    pub.sendMessage('topc')  # creates 'topc' topic; no listener will receive

These can lead to hard-to-isolate bugs as some listeners never get the messages. 
To trap such typos, use :py:func:`pub.setTopicUnspecifiedFatal(true)`, and 
specify all allowed topics at application startup by registering a Topic 
Definition Provider via :py:func:`pub.addTopidDefnProvider()`. Both above 
typos will then lead to PyPubSub
raising :py:class:`TopicDefnError`. Note: a provider can easily be created via the 
:py:func:`pub.exportTopicTreeSpec()`.

