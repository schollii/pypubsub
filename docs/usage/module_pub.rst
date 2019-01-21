Pub Module
==========

.. automodule:: pubsub.pub
      
.. autodata:: VERSION_API

    The PyPubSub API version. This is deprecated. The only valid value currently is the integer 4.
    Previously, versions 1, 2 and 3 API could also be activated in PyPubSub before importing pub, in
    which case pub.VERSION_API had the corresponding value. 
    
    
Sending Messages
----------------

Sending messages is achieved via the following function: 

.. autofunction:: sendMessage(topicName, **kwargs)

The following exception may be raised when sending a message, if the message 
data does not comply with the Message Data Specification for the topic: 

.. autoexception:: SenderMissingReqdMsgDataError
    :show-inheritance:
.. autoexception:: SenderUnknownMsgDataError
    :show-inheritance:

**Advanced use:**

The following would typically only be useful in special circumstances, such as 
if PyPubSub's default Publisher must be accessed, on or more separate instances of
Publisher is required, and so forth. 

.. autofunction:: getDefaultPublisher
.. autoclass::    pubsub.core.Publisher
    :noindex:

    See :py:class:`pubsub.core.Publisher` for details.


Receiving Messages
------------------

The following functions are available for controlling what callable objects 
(functions, methods, or class instances with a __call__ method) will get 
called when messages are generated: 

.. autofunction:: subscribe(listener, topicName)
.. autofunction:: unsubscribe(listener, topicName)
.. autofunction:: unsubAll(topicName=None, listenerFilter=None, topicFilter=None)
.. autofunction:: isSubscribed

The following exceptions are relevant:

.. autoexception:: ListenerMismatchError
    :show-inheritance:
    
.. autoexception:: MessageDataSpecError
    :show-inheritance:
    
.. py:data:: AUTO_TOPIC

    Use this as default parameter in a listener's signature: the listener 
    will be given the Topic object of the message. 

The following additional functions may be useful during debugging: 

.. autofunction:: isValid
.. autofunction:: validate
.. autoexception:: TopicDefnError
    :show-inheritance:
    
**Advanced use:**

The following are not typically required but can be useful in certain circumstances, 
especially during debugging: 

.. autoclass:: pubsub.core.Listener
    :noindex:

    See :py:class:`pubsub.core.Listener` for details.

.. autofunction:: pubsub.core.getListenerID


Topics
------

In most cases, topics are used by name in dotted string format. The following 
may be useful for basic PyPubSub use:

.. autoexception:: TopicNameError
    :show-inheritance:

**Advanced use:**

Some advanced uses of PyPubSub, especially (but not only) for debugging a PyPubSub-based
application, could require access to the associated Topic instance, topic tree 
manager, special topic-related constants, or other helper functions and classes. 

.. autoclass:: TopicTreeTraverser

.. py:data:: ALL_TOPICS

    Name of topic that is root of topic tree. Subscribe a listener
    to this topic to get all PyPubSub messages. Use \**kwargs to receive
    all message data, regardless of topic. 
    
.. py:data:: topicTreeRoot    

    The topic object that is parent of all root topics. The name of this 
    topic is pub.ALL_TOPICS.
    
.. py:data:: topicsMap 

    The dictionary that maps topic names to Topic objects.

**Advanced use:**

The following are not typically required but can be useful in certain circumstances, 
such as during debugging: 

.. autofunction:: getDefaultTopicMgr
.. autoclass:: pubsub.core.TopicManager
    :noindex:

    See :py:class:`pubsub.core.TopicManager` for details.

.. autoclass:: pubsub.core.Topic
    :noindex:
    
    See :py:class:`pubsub.core.Topic` for details.
                      
Listener Exception Handling
---------------------------

Listeners that leak exceptions are typically burried deep into the stacktrace, and 
can cause an application to abort. The following may simplify the task of providing 
useful error messages from misbehaved listeners, without interrupting the application
or even the PyPubSub send-message:

.. autofunction::  getListenerExcHandler()
.. autofunction::  setListenerExcHandler(handler)
.. autoclass::     IListenerExcHandler
.. autoexception:: ExcHandlerError
    :show-inheritance:

See :mod:`pubsub.utils.exchandling` for ready-made exception handlers which may fit your 
requirements. 


PyPubSub Tracing (aka Notification)
-----------------------------------

While debugging an application it may be useful to trap some of PyPubSub's activity:

.. autoclass::    INotificationHandler
.. autofunction:: addNotificationHandler(handler)
.. autofunction:: clearNotificationHandlers()
.. autofunction:: setNotificationFlags(**kwargs)
.. autofunction:: getNotificationFlags()

See :mod:`pubsub.utils` for some ready-made notification handlers 
which may fit your requirements. 


Topic Specification 
-------------------

Topic definition, documentation, and message data specification (MDS):

.. autoexception:: TopicDefnError
    :show-inheritance:

.. autofunction:: exportTopicTreeSpec

.. autofunction:: setTopicUnspecifiedFatal(newVal=True, checkExisting=True)

.. autofunction:: addTopicDefnProvider(providerOrSource, format=None)
.. autofunction:: getNumTopicDefnProviders()
.. autofunction:: clearTopicDefnProviders()
.. autofunction:: instantiateAllDefinedTopics(provider)
.. autoexception:: UnrecognizedSourceFormatError
    :show-inheritance:

.. autodata:: TOPIC_TREE_FROM_MODULE

    Provide to pub.addTopicDefnProvider() as value for format parameter when the 
    source is a module which has been imported. The module can contain any 
    number of classes, the names of which correspond to root topics.
    
.. autodata:: TOPIC_TREE_FROM_CLASS

    Provide to pub.addTopicDefnProvider() as value for format parameter when the 
    source is a class. The class contains, as nested classes, the root topics (and 
    those contain nested classes for subtopics, etc).
    
.. autodata:: TOPIC_TREE_FROM_STRING

    Provide to pub.addTopicDefnProvider() as value for format parameter when the 
    source is a string. The string contains Python code that defines one class 
    for each root topic (and those contain nested classes for subtopics, etc).
    

**Developer**: 

The following are useful to extend the capabilities of PyPubSub to support more
topic definition providers or serialization formats for the builtin provider:

.. autoclass:: pubsub.core.ITopicDefnProvider
.. autoclass:: pubsub.core.ITopicDefnDeserializer
.. autoclass:: pubsub.core.TopicDefnProvider
    :show-inheritance:

