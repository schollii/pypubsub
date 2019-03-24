.. _label-basic-tasks:

Basic PyPubSub Tasks
====================

Several essential tasks supported by PyPubSub

.. contents:: In this section:
   :depth: 2
   :local:


Subscribing to Topics
---------------------

Every message that can be sent via PyPubSub is of a specific topic, just as every
object in Python is of a specific type. 

Use ``pub.subscribe(callable, 'topic-path')`` to subscribe callable 
to all messages of given topic or any of its subtopics. 

Callable
^^^^^^^^

The callable can be:

* any function
* any method
* any class instance that defines ``__call__`` method

Hence given the following definitions::
    
    def function(): pass
    
    class Foo:
        def method(self): pass
        
        @staticmethod
        def staticMeth(): pass
        
        @classmethod
        def classMeth(cls): pass
        
        def __call__(self): pass
        
    foo = Foo()

the following callables could be subscribed to a PyPubSub message topic::

    function
    foo.method
    foo
    Foo.staticMeth
    Foo.classMeth

PyPubSub holds listeners by weak reference so that the lifetime of the callable
is not affected by PyPubSub: once the application no longer references the callable,
it can be garbage collected and PyPubSub can clean up so it is no longer registered
(this happens thanks to the weakref module). Without this, it would be imperative 
to remember to unsubscribe certain listeners, which is error prone; they would end up 
living until the application exited. 

A nice example of this is a 
user control (widget) in a GUI: if a method of the user control is registered 
as listener in PyPubSub, and the control is discarded, the application need not
explicitly unregister the callable: the weak referencing will allow the widget
to be garbage collected; otherwise, it would remain visible until explicit 
unsubscription. 

.. warning::

    One caveat that results from this useful feature is that all callables 
    that subscribe to topics must be referenced from outside PyPubSub. For instance,
    the following will silently unsubscribe on return from pub.subscribe()::
    
        def listener(): pass
        def wrap(fn): 
            def wrappedListener():
                fn()
            return wrappedListener
        pub.subscribe(wrap(listener), 'topic')
        
    since wrap() returns an object which only PyPubSub references: the wrappedListener
    gets garbage collected upon return from subscribe(). It is 
    possible to verify that the stored listener is indeed dead::
    
        ll,ok = pub.subscribe(wrap(listener), 'topic')
        print ll.isDead() # prints True
        
    Compare without wrapping::
        
        ll,ok = pub.subscribe(listener, 'topic')
        print ll.isDead() # prints False
        
    Fix by storing a strong reference to wrappedListener::
    
        ww = wrap(listener) # creates strong reference
        ll,ok = pub.subscribe(ww, 'topic')
        print ll.isDead() # prints False


.. _label-topic-name:

Topic Name
^^^^^^^^^^

Every topic has a name and a path. The name can contain any character a-z, A-Z, 0-9 and 
_&%$#@ and the hyphen. Valid examples are::

    'asdfasdf'
    'aS-fds0-123'
    '_&%$#@-abc-ABC123'

Other characters will lead to an exception or undefined behavior. 

Topics form a hierarchy: 

* every topic can be child of a "parent" topic
* a topic that does not have a parent topic is a "root" topic
* every topic can have one or more "children" i.e. sub topics

The fully qualified topic name is therefore the path through the topic hierarchy. 
The path separator is '.'. Hence given the following topic hierarchy::

    root-topic-1
        sub-topic-2
            sub-sub-topic-3
            
the following subscriptions could be valid::

    pub.subscribe(callable, 'root-topic-1')
    pub.subscribe(callable, 'root-topic-1.sub-topic-2')
    pub.subscribe(callable, 'root-topic-1.sub-topic-2.sub-sub-topic-3')

.. _label-MDS:

Message Data
^^^^^^^^^^^^

Messages of a given topic can carry data. Which data is required and which 
is optional is known as the *Message Data Specification* for the topic, or MDS for short.
Unless your application explicitly defines the MDS for every topic in the hierarchy,
PyPubSub infers the MDS of each topic based on the first pub.subscribe() or
the first pub.sendMessage() for the topic, whichever occurs first during 
an application run. Once defined, a topic's MDS never changes (during a run).

Examples of MDS inferred from a call to pub.subscribe():

============================================ =================================
Callable signature                           MDS (inferred)
============================================ =================================
``callable(arg1)``                           - required: arg1
                                             - optional: none
``callable(arg3=1)``                         - required: none
                                             - optional: arg3
``callable(arg1, arg2, arg3=1, arg4=None)``  - required: arg1, arg2
                                             - optional: arg3, arg3
============================================ =================================
                                
All subsequent calls to pub.subscribe() for the same topic or any subtopic 
must be consistent with the topic's MDS.
If a subscription specifies a callable that does not match the given topic's MDS,
PyPubSub raises an exception. Therefore, the pub.subscribe() calls above
*could* be valid; they *will* be valid if the given callable satisfies the 
given topic's MDS.

Examples of subscriptions: assume MDS of topic 'root' is
required=arg1, optional=arg2, then pub.subscribe(callable, 'root') for 
the following callable signatures are ok:

=============================== ==== =================================
Callable                        OK    Why
=============================== ==== =================================
callable(arg1, arg3=1)          Yes  matches MDS
callable(arg1=None, arg3=None)  Yes  signature is less restrictive 
                                     than MDS, and default value
                                     are not part of MDS
callable(arg1)                  No   arg2 could be in message, yet
                                     callable does not accept it
callable(arg1, arg2)            No   callable requires arg2, but MDS
                                     says it won't always be given in 
                                     message
=============================== ==== =================================

A callable subscribed to a topic is a listener. 

Note that the default value for an optional message data is not part 
of the MDS. Each listener can therefore decide what default value to use if
the data is not provided in the message. 


Sending messages
----------------

Use ``pub.sendMessage('topic-path-name', **data)`` to send a message with the 
given data. The topic path name is a dot-separated sequence of topic names 
from root to topic (see :ref:`label-topic-name`). 

The message is sent to all registered listeners of given topic, parent
topic, and so forth up the "topic tree", by calling each listener, in 
turn, until all listeners have been sent the message and data. A listener
must return before the next listener can be called. The order of listeners
(within a topic or up the tree) is not specified. The sender should not 
make any assumptions about the order in which listeners will be called, 
or even which ones will be called. If a listener leaks an exception, 
PyPubSub catches it and interrupts the send operation, unless an exception
handler has been defined. This is discussed in :ref:`label-exchandling`. 

Message Data
^^^^^^^^^^^^

The data must satisfy the 
topic's MDS, and all arguments must be named. So for a topic 'root' with MDS
of arg1, arg2 required and arg3 optional, the send command would have the form::

    pub.sendMessage('root', arg1=obj1, arg2=obj2, arg3=obj3)
    
One consequence of this is that the order of arguments does not matter::

    pub.sendMessage('root', arg3=obj3, arg2=obj2, arg1=obj1)

is equally valid. But 
::

    pub.sendMessage('root', obj1, obj2, arg3=obj3)
    
is not allowed. 

Only the message data relevant to a topic is sent to the listeners of the 
topic. For example if topic 'root.sub.subsub' has a MDS involving data arg1, arg2 and
arg3, and topic 'root' has only arg1, then listeners of 'root.sub.subsub' topic
will get called with arg1, arg2, and arg3, but listeners of 'root' will 
get called with the arg1 parameter only. The less specific topics have less
data. 

Since messages of a given topic are sent not only to listeners of the topic 
but also to listeners of topic up the topic tree, PyPubSub requires that subtopic
MDS be the same or more restrictive as that of its parent: optional arguments can become
required, but required arguments cannot become optional. Indeed if 'root' 
messages require arg1, then 'root.sub' must also require it; otherwise a 
message of type 'root.sub' could be sent without an object for arg1, and 
once the 'root' listeners received the message, they could find the required
parameter missing. If 'root' messages have arg2 as optional data, then 
'root.sub' can be more restrictive and require it. 

Examples of subtopic MDS: assume topic 'root' has MDS required arg1 and
optional arg2. Then following 'root.sub' MDS would be

==== ================= ==== =========================================
Case MDS extended by   OK    Why
==== ================= ==== =========================================
1    + required arg3   Yes  Extends MDS of 'root'
     + optional arg4
2    + optional arg3   No   Less restrictive than 'root': arg3 
     + optional arg4        could be missing from 'root.sub' message
==== ================= ==== =========================================

Topic as Message Data
^^^^^^^^^^^^^^^^^^^^^

If a listener requires to know the topic of the message, a specially named 
default value ``pub.AUTO_TOPIC`` can be used for one of its call parameters:
at call time, PyPubSub will replace the value by the pub.TopicObj object for the topic.
It can be queried to find the topic name via Topic.getName()::

    def listener(topic=pub.AUTO_TOPIC):
        print "real topic is", topic.getName()
    pub.subscribe(listener, "some_topic")
    pub.sendMessage("some_topic") # no data 
        
This allows each listener to define whether it needs the topic information 
(rarely the case). Therefore, it is not part of the MDS. In the above
example, the MDS for 'some_topic' is empty.


Sending vs Broadcasting
^^^^^^^^^^^^^^^^^^^^^^^

The pub.sendMessage() shares some similarities and differences
with "broadcasting". Some similarities: 

* All callables subscribed to the topic will receive the 
  message; in broadcasting, all receivers tuned in to the emitter 
  frequency will receive the data. Hence the topic is akin to 
  the radio frequency of the broadcast. 
* The sender has no knowledge of which listeners are subscribed 
  to a topic; in broadcasting, the emitter does not
  know which receivers are "tuned in"
* The order in which listeners receive the broadcast is 
  undefined. In broadcasting, distance to the emitter affects when 
  the receiver will get the message, and the emitter has no knowledge
  of where receivers are located, so it can't know which receiver 
  will hear the message first. 
* The listener does not know the source of messages. In broadcasting, 
  the receiver has no way of knowing which emitter is the source of a 
  given message: it will capture all messages from different emitters 
  sa though that had all been generated by the same emitter, 
  as long as they are of the same frequency. 
* Listeners to not send any data back to the sender as part of the
  message delivery. In broadcasting, the receiver does not send any 
  data back to the emitter as part of the message. 
  
Some differences: 

* A message sent to a listener must be processed before it can be sent
  to another listener of same topic. In broadcasting, all receivers 
  can process the message simultaneously. 
* The listener cannot send data back to the sender: the sender is the 
  line of code that calls pub.sendMessage(), this is not a callable nor
  is it subscribed to the topic of the message sent. In broadcasting, 
  the receiver can transmit over the same frequency as received message, 
  and the emitter could (if it has reception capability and is tuned to 
  same frequency) read the message. 
* Listeners of parent topics will get messages for subtopics. In 
  broadcasting, there is no analogy of "sub-frequencies". 


Handling messages
-----------------

A callable subscribed to a topic receives a message by being called. 
Assuming that the send command is::

    pub.sendMessage('topic-path-name', **data)

then all listeners subscribed to the named topic will get called with 
the given \**data dictionary, as well as all listeners of the topic's 
parent topic, and so forth until the root topic is reached. 

.. warning::

    A listener should not make any assumptions about:

    * The order of calls of listeners subscribed to same or other topics
    * Where the message originates


Message Data
^^^^^^^^^^^^

Only the
portion of data that is relevant to the topic is given to each listener.
Assume the following topic branch of the hierarchy::

    tt: listeners a and b; MDS is r=arg1, o=arg4
        uu: listeners c and d; MDS is r=(arg1, arg2), o=(arg4, arg5)
            vv: listeners e and f; MDS is r=(arg1, arg2, arg3), o=(arg4, arg5, arg6)
            
then ``pub.sendMessage('root-topic', arg1=1, arg2=2, arg3=3, arg4=4, arg5=5, arg6=6)``
will call

* ``e(arg1=1, arg2=2, arg3=3, arg4=4, arg5=5, arg6=6)``; same with f; implicitly the topic is tt.uu.vv
* ``c(arg1=1, arg2=2, arg4=4, arg5=5)``; same with d; implicitly the topic is tt.uu
* ``a(arg1=1, arg4=4)``; same with b; implicitly the topic is tt

As stated in the 'Sending Messages' section, the order in which the listeners are called is not 
specified; your application should not make any assumptions about this order. 