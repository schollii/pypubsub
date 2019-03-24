Debugging an application
========================

.. contents:: In this section:
   :depth: 2
   :local:


Types of Errors
---------------

While developing an application that uses PyPubSub, calls to PyPubSub
functions and methods may raise an exception. These are discussed in:

.. toctree::

   types_of_errors
   

Notification: Tracking PyPubSub activity
----------------------------------------

PyPubSub can call a specified handler every time it performs a certain task:

- *subscribe*:    whenever a listener subscribes to a topic
- *unsubscribe*:  whenever a listener unsubscribes from a topic
- *deadListener*: whenever PyPubSub finds out that a listener has died
- *send*:         whenever the user calls sendMessage()
- *newTopic*:     whenever the user defines a new topic
- *delTopic*:     whenever the user undefines a topic

A notification handler must adhere to the pub.INotificationHandler::

    import pubsub.utils
    class MyNotifHandler(INotificationHandler):
        def onSendMessage(...): 
            ...
    
    pub.addNotificationHandler( MyNotifHandler() )
    

A simple handler class is available already in ``pubsub.utils``: 
``notification.NotifyByPubsubMessage``. 
This handler takes each notification received and generates a PyPubSub
message of a "pubsub." topic named after the operation, such as "pubsub.subscribe". 
To use notification via this notifier, you must register one or more 
listeners for the "pubsub.*" topics of interest. 

A utility function is available from pubsub.utils for the most common case::

    from pubsub.utils import notification
    notification.useNotifyByPubsubMessage()

.. _label-exchandling:

Naughty Listeners: Trap Exceptions
----------------------------------

A sender has no way of knowing what can go wrong during message handling by the 
subscribed listeners. As a result, a listener must not raise any exceptions (or 
rather, must not let any exceptions escape): if an exception does escape a 
listener, it interrupts the ``pub.sendMessage()`` call such that some listeners may 
not be sent the message. Putting a try/except clause around every sendMessage is 
typically not practical. 

Since exceptions are common during application development (bugs due to 
invalid arguments, failed assertions, etc.), PyPubSub provdes a hook to register
a 'listener exception' handler: whenever a listener raises an exception, 
PyPubSub then sends it to the handler, and continues with the send operation
until all listeners have received the message. The handler might print it to
a log file, output a message in a status bar, show an error box, etc. The 
handling itself is very application-specific, hence this strategy. 

The handler must adhere to the ``pub.IListenerExcHandler`` protocol. An instance
of the handler can be given to ``pub.setListenerExcHandler()``.


Listen for messages from all topics
-----------------------------------

PyPubSub defines a special topic named pub.ALL_TOPICS. A listener that subscribes to
this topic will receives all messages of every topic. By default, the listener
will not receive any data since pub.ALL_TOPICS is the parent of all root topics: 
its MDS must be empty. 

However, any listener that is a callable
with a "catch-all" \**kwargs parameter will be given all message data. Moreover, 
PyPubSub sends the topic object automatically with the message data if it
finds that listener accepts a keyword argument with a default value of pub.AUTO_TOPIC. 
Together, these can be used to obtain complete information about all messages::

    >>> def snoop(topicObj=pub.AUTO_TOPIC, **mesgData):
    >>>     print 'topic "%s": %s' % (topicObj.getName(), mesgData)
    >>>     
    >>> pub.subscribe(snoop, pub.ALL_TOPICS)
    (<pubsub.core.listenerimpl.Listener instance at 0x01A040A8>, True)
    >>> pub.sendMessage('some.topic.name', a=1, b=2)
    topic "some.topic.name": {'a': 1, 'b': 2}


Using the pub.Listener class
----------------------------

Every callable that is subscribed via pub.subscribe() is wrapped in a 
pub.Listener instance returned by this function. This class has several 
useful functions such as name(), typeName(), module(), and isDead(). 
For example::

    >>> def snoop(topicObj=pub.AUTO_TOPIC, **mesgData):
    >>>     pass
    >>>     
    >>> pubListener, first = pub.subscribe(snoop, pub.ALL_TOPICS)
    >>> assert first == true # since first time subscribed
    >>> assert pubListener.isDead() == false
    >>> assert pubListener.wantsTopicObjOnCall() == true
    >>> assert pubListener.wantsAllMessageData() == true
    >>> print pubListener.name()
    snoop_2752
    >>> print pubListener.name()
    snoop


Doing something with every topic 
--------------------------------

Derive from pub.ITopicTreeVisitor and give instance to an instance of 
pub.TopicTreeTraverser, then call traverse() method. For example, assume
a callable 'listener' has been subscribed to several topics. An easy way 
to verify all topics subscribed to use this:

    >>> class MyVisitor(pub.ITopicTreeVisitor):
    >>>    def __init__(self, listener):
    >>>        self.subscribed = []
    >>>        self.listener = listener
    >>>    def _onTopic(self, topicObj):
    >>>        if topicObj.hasListener(self.listener):
    >>>            self.subscribed.append(topicObj.getName())
    >>>
    >>> tester = new MyVisitor(listener)
    >>> traverser = pub.TopicTreeTraverser( tester )
    >>> traverser.traverse(pub.getDefaultTopicTreeRoot())
    >>> print tester.subscribed
    ['topic-name', 'topic-name2', ...]


Printing Topic Tree
-------------------

See pubsub.utils.printTreeDocs().

    
