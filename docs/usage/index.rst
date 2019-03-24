Use
=======

If you are new to PyPubSub, you will likely want to start with :ref:`label-usage-basic`.
If you want a quick start, jump the :ref:`label-quick-start` section. 

If you develop an application that uses PyPubSub, whether it is prototype or production 
quality code, if it is more than just an experiment you will find that it can become
challenging to debug the flow of messages. This is because the decouping can make the 
link between causes and effects challenging to identify. Also, you need better control 
over error handling since an exception in a listener cannot be handled by a sender; 
and more maintainability via documentation of message structure so it remains easy
to remember what payload can be passed with messages, and so PyPubSub can verify that
a listener is compatible with a sender. This is when you turn to the 
:ref:`label-usage-advanced` section. 

.. contents:: 
   :depth: 1
   :local:

.. toctree::
   :maxdepth: 2
   
   usage_basic
   usage_advanced
   howtos/index
   reference
