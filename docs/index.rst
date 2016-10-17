.. PyPubSub documentation master file, created by
   sphinx-quickstart on Mon May 20 21:24:10 2013.

Welcome to PyPubSub's Home Page!
====================================

This is the documentaiton for the PyPubSub project. This Python project defines
a package called 'pubsub' which provides a publish - subscribe API to facilitate
event-based programming and decoupling of components of an application. Using
the publish - subscribe pattern in your application
can dramatically simplify its design and improve testability. Robin Dunn, the 
creator of wxPython where the pubsub package was born, summerizes PyPubSub nicely:

    Basically you just have some part(s) of your program 
    subscribe to a particular topic and have some other part(s) 
    of your program publish messages with that topic.  All the 
    plumbing is taken care of by pubsub.  -- *Robin Dunn, Jun 2007*

The Publish - Subscribe pattern, as implemented by pubsub, provides the following 
contract between sender and receiver: 

1. Message Sender: The sender of a pubsub message is the ccode that calls pub.sendMessage().
2. Message Topic: 
   a. Every message has a "type": it corresponds to its "topic", a string name
   b. Topics form a hierarchy. A parent topic is more generic than a child topic. 
3. Message Listener: All message listeners are callables that
   get registered with pubsub in order to receive messages of a given topic
4. Message Delivery: 

   a. Messages sent will be delivered to all registered listeners for a given topic,
      and all listeners of the parent topic, etc until the root of all topics is reached
      (hence the root of all topics, called ALL_TOPICS, receives all messages)
   b. Sequence of delivery: unspecified and can change at any time; do not depend on it
   c. Messages are delivered synchronously: a listener must return or throw an exception
      before the message is delivered to the next listener
   d. A message sent will be delivered to all registered listeners of the message topic
      before control is returned to the sender

5. Message Constness: message contents must be left unchanged by any listeners
6. Message Direction: a message is one-way from sender to listener; it cannot be used by
   the listener to transmit data back to the sender
7. Message Source: Pubsub does not provide any information to the listeners regarding the
   origin (aka source, or provenance) of a message

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

