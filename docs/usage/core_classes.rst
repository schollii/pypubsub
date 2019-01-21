Core Classes
============

The following classes are useful for advanced use of PyPubSub:

- pubsub.core.Listener
- pubsub.core.TopicObj
- pubsub.core.TopicManager
- pubsub.core.Publisher

It is not typically necessary to know about or use these: the pub module instantiates a 
default Publisher, which contains a TopicManager, which generates a Topic object
for every topic used. The Publisher instance returns a Listener instance from subscribe, 
wrapping the given callable with PyPubSub-relevant meta-data about the callable.


Publisher
---------

.. autoclass::  pubsub.core.Publisher
    :members:
    :inherited-members:

TopicManager
------------

.. autoclass::  pubsub.core.TopicManager
    :members:
    :inherited-members:

Topic
-----

.. autoclass::  pubsub.core.Topic
    :members:
    :inherited-members:

Listener
--------

.. autoclass::  pubsub.core.Listener
    :members:
    :inherited-members:

