.. PyPubSub documentation master file, created by
   sphinx-quickstart on Mon May 20 21:24:10 2013.

Welcome to PyPubSub's Home Page!
====================================

This is the documentaiton for the PyPubSub project. This Python project defines
a package called 'pubsub' which provides a publish - subscribe API to facilitate
event-based programming and decoupling of components of an application via the
Observer pattern. PyPybSub originated in wxPython around y2k but has been
standalone since 2006, and has been on PyPI since then. The code was hosted on
SourceForget.net from 2007 to 2016, and the code is now hosted on github. The
code is very mature and stable. See :ref:`label-history` for details on its history
and :ref:`label-roadmap` for possible future work.

Using the Observer pattern in your application
can dramatically simplify its design and improve testability. Robin Dunn, the 
creator of wxPython where the pubsub package was born, summerizes PyPubSub nicely:

    Basically you just have some part(s) of your program 
    subscribe to a particular topic and have some other part(s) 
    of your program publish messages with that topic.  All the 
    plumbing is taken care of by pubsub.  -- *Robin Dunn, Jun 2007*

The Publish - Subscribe API provided by pubsub has the following characteristics:

1. Message Sender: The sender of a pubsub message is the ccode that calls pub.sendMessage().
2. Message Topic: 
   a. Every message is specific to a "topic", defined as a string name;
   b. Topics form a hierarchy. A parent topic is more generic than a child topic.
3. Message Data: any keyword arguments used by the sender, pub.sendMessage(topic, \**data);

   a. A topic may have no associated message data, or may have any mixture of required
      and optional data; this is known as its Message Data Specification (MDS);
   b. The MDS of a child topic cannot be more restrictive than that of a parent topic;
   c. Once the MDS is set for a topic, it never changes during the runtime of an application.

4. Message Listener: All message listeners are callables that get registered with pubsub
   in order to receive messages of a given topic, and must have a signature that is
   compatible with the topic's MDS.
5. Message Delivery:

   a. Messages sent will be delivered to all registered listeners of a given topic; this
      includes listeners of the topic, parent topic, etc. Hence the root of all topics
      (called ALL_TOPICS) receives all messages;
   b. Sequence of delivery is unspecified and can change at any time; do not depend on it!
   c. Messages are delivered synchronously: a listener must return or throw an exception
      before the message is delivered to the next listener;
   d. A listener that raises an exception does not prevent remaining listeners from
      receiving the message;
   e. A message sent will be delivered to all registered listeners of the specified topic
      before control is returned to the sender.

6. Message Immutability: message contents must be left unchanged by listeners, but pypubsub
   does not verify this.
7. Message Direction: a message is one-way from sender to set-of-listeners; pubsub does not
   support "answering" with a response from each listener to the sender. This could, of course,
   be achieved by having the sender include a callback as message data, and each listener
   calling that callback with agreed-upon data, but this (typically) increases coupling.
8. Message Source: Pubsub does not provide any information to the listeners regarding the
   origin (aka source, or provenance) of a message. The sender could, of course, include such
   information with the message data, but this is *not* recommended as it defeats the purpose
   of the Observer pattern.

Here is a schematic representation of the role of pubsub during message sending and delivery:

.. image:: pubsub_concept.png
   :alt: Sketch showing how pubsub fits into a Python application
   :align: center
   :width: 450px

..
   
Contents:

.. toctree::
   :maxdepth: 2

   about
   installation
   usage/index
   development/dev_index

   
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

