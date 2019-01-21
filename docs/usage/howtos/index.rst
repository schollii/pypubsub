How Tos
=======

This section provides "recipes" for various tasks such as migrating an 
application from one PyPubSub version or messaging protocol to another.


.. _label-migrations:

Migrations
----------

In the very first version of PyPubSub, v1, message data was transported via a
single instance of a class called Message. This had several important limitations,
most importantly the inability to validate whether the correct data fields
were being included in a message sent.

In PyPubSub v3, a new protocol was implemented, and was named kwargs. This was
not compatible with v1, but v3 made it possible to configure the imported
pubsub to select either the arg1 protocol or the kwargs protocol, and to configure
PyPubSub to help with transition from one to the other.

PyPubSub v4 only supports the kwargs protocol. If you want to upgrade your
application from using PyPubSub v1 or v3 to v4 and it uses the arg1 protocol,
you will have to do the transition via PyPubSub 3.3, as explained at length
in the documentation for that version (specifically, see the section
`label-migrations`)

Please post on the list for any additional support needed on this topic.
