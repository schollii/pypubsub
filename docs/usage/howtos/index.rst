How Tos
==========

This section provides "recipes" for various tasks such as migrating an 
application from one pypubsub version or messaging protocol to another. 


.. _label-migrations:

Migrations
-----------

Section :ref:`label-pubsub_versions` describes the 2 mains versions of 
pypubsub that have existed: v1 and v3. Section :ref:`label-msg_protocols`
describes the two messaging protocols that exist in v3: kwargs (the default) 
and arg1, compared to v1 which only support the arg1 protocol. The v1 API is no 
longer part of pubsub, so two migrations of particular interest are:

:v1 to v3/arg1: 
    typically wxPython users (since v1 originated in wxPython) wanting to 
    take advantage of the latest version of pypubsub, but without changing 
    the messaging protocol, so as to minimize the amount of migration work.
    See :ref:`label-upgrade_for_wx`.

:v3/arg1 to v3/kwargs:
    pypubsub users of arg1 messaging protocol wanting to take advantage of 
    the more robust kwargs protocol. See section :ref:`label-trans_arg1_to_kwargs`.

.. toctree:: 
    :hidden:
    
    arg1_to_kwargs.rst
    upgrade_v1tov3.rst