
.. _label-upgrade_for_wx:

Upgrade from arg1
===================

This section describes how to upgrade an application that uses
the legacy PyPubSub v1 API (which was default in wxPython until wxPython v2.9
and only supported the arg1 messaging protocol) to use the latest pubsub API, 
but without changing the messaging protocol. 

Good news: Most pubsub users will only need to change some import statements. 
For those who made use of other parts of the v1 API, the :ref:`label_differences`
section also lists all the differences between the two API.

Verify v1 in use:

  #. start a python interpreter session (same version as used by your app)
  #. copy your app's pubsub import statement; for instance ::

       >>> from wx.lib.pubsub import pub

  #. then :

       >>> print pub.VERSION_STR
       
Next step depends on printout: 

* If the response starts with "1", you are using v1. Follow the steps below. 
* If starts with "3", you are already using the latest pubsub API, this section is not 
  relevant. Consider having a look at :ref:`label-trans_arg1_to_kwargs`. 
* For anything else, post to the PyPubSub help forum (see URL on the Installation/Support 
  page).


Suggested Steps
----------------

#. In your application's main script (or at very least, before the first 
   pubsub import that your application will execute), import setuparg1 from pubsub: 

        from wx.lib.pubsub import setuparg1
       
#. Do a search/replace of ``Publisher.`` for ``pub.``
#. Run your application and check if all works well: if so, you are done!
#. Otherwise, look at the :ref:`label_differences` section
#. If you still have issues, post on the Help forum. 

Example
----------

For example, if yourApp.py is your application's startup script and
contains ::

    from wx.lib.pubsub import Publisher

    Publisher.sendMessage('hello')

then after having followed the migration steps, the above lines would be ::

    from wx.lib.pubsub import setuparg1
    from wx.lib.pubsub import pub

    pub.sendMessage('hello')

Notes:

- If you are using wxPython version <= 2.8.10.0, wx.lib.pubsub is a module
  which adheres to v1 API but does not support v3 API.
- If your application runs without a console window and you don't
  catch all Exception exceptions, you may not
  have time to see the exception traceback that the Python interpreter
  prints at exit. Start your GUI app from a console, or have a
  catch-Exception and print the error in your GUI.

See the test file :file:`tests/trans1to3/test_trans_step_1.py` in the
source distribution for an example application after this step has
been executed.


.. _label_differences:

Differences
--------------

Each subsection describes a difference between the v1 and v3 API with same 
messaging protocol (arg1).

Main access point
^^^^^^^^^^^^^^^^^^^

The main interface to pubsub in v1 was via ``pubsub.Publisher``, which was a
singleton instance of a PublisherClass class. Pubsub supported the following
ways of accessing pubsub functionality:

Version 1.x::

  from wx.lib.pubsub import Publisher
  Publisher.function(...)     # OR:
  Publisher().function(...)

Version >= 3.0::

  from wx.lib.pubsub import pub    # OR:
  from pubsub import Publisher # alias for "pub"
  pub.function() # only!

Ie,

- the (IMO) clunky syntax of ``Publisher().function()`` is no longer
  supported in pubsub after v1. A global search replace will easily take
  care of this.
- a shorter form of import is available, ``from pubsub import pub``


sendMessage
^^^^^^^^^^^^^

Version 1.x::

  sendMessage(topic = ALL_TOPICS, data  = None, onTopicNeverCreated=None)

Version >= 3.0::

  sendMessage(topicName, data  = None)

Changes:

- In v1, ``sendMessage()``, without any arguments, can be used. This will send
  a message of topic "ALL_TOPICS". In v3, you must explicitly give
  ``pub.ALL_TOPICS`` for the ``topicName`` argument.
- In v1, ``onTopicNeverCreated`` is a callback that can be given to
  sendMessage, to call if the topic doesn't yet exist, to help with
  debugging of messages. This is limited for many reasons so it has been 
  removed. There are several way of replacing it in v3: 
  
  - via the pubsub notification mechanism: you derive
    a class from ``pubsub.utils.IgnoreNotificationsMixin``, override the
    the ``notifyNewTopic()`` to do the same as ``onTopicNeverCreated``,
    and call ``pubsub.addNotificationHandler( YourHandler() )``.
  - by printing the topic tree


subscribe
^^^^^^^^^^^^^

Version 1.x::

  subscribe(listener, topic = ALL_TOPICS)

Version >= 3.0::

  subscribe(listener, topicName)

Change: In v1, ``subscribe(listener)`` can be used to subscribe a callable
to the "ALL_TOPICS" topic. In v3, you must explicitly give
``pub.ALL_TOPICS`` for the ``topicName`` argument, ie a topic name is
always required. This follows the "explicit is better" philosophy of Python.


unsubscribe
^^^^^^^^^^^^^

Version 1.x::

  unsubscribe(listener, topics=None)

Version >= 3.0::

  unsubscribe(listener, topicName)

Change: In v1, ``unsubscribe(listener)`` can be used to unsubscribe a
callable from all topics that it is subscribed to. This is redundant
since this functionality is available via ``unsubAll`` function, so this
capability has been removed and a topic name is always required.
Furthermore, in v1 the ``topics`` argument could be a list of topic names,
a convenience to unsubscribe a listener from several topics. Again, this
is available via the unsubAll function so it has been removed.
Change any calls of the form ``unsubscribe(listener)`` or
``unsubscribe(listener, list of topics)`` to use ``unsubAll``


isSubscribed
^^^^^^^^^^^^^

Version 1.x::

    isSubscribed(listener, topic=None)

Version >= 3.0::

    isSubscribed(listener, topicName)

Change: In v1, leaving topic=None cause ``isSubscribed(listener)`` to check
whether listener was subscribed to anything. This test is no longer
available via isSubscribed post v1 due to the way listeners are registered.
However, ``pub.getDefaultTopicMgr().getTopics(listener) != []`` provides the 
same answer.


unsubAll
^^^^^^^^^^^^^

Version 1.x::

    unsubAll(topics = None, onNoSuchTopic = None)

Version >= 3.0::

    unsubAll(topicName = None, listenerFilter = None, topicFilter = None)

Change: as with sendMessage, the callback is no longer accepted. The
equivalent functionality could be obtained similarly, see the sendMessage
discussion, specifically, about pubsub notification handling.


getAssociatedTopics
^^^^^^^^^^^^^^^^^^^^^

Version 1.x::

  returns list of topic names (names in tuple format)

Version 3.0 to 3.1::

  returns list of pub.Topic objects

Version >= 3.2::

  same as previous, but must be obtained from pubsub.core rather than pub

validate
^^^^^^^^^^^^^

Version 1.x::

  raises TypeError

Version >= 3.0::

  raises ListenerMismatchError


getMessageCount, getDeliveryCount
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both are no longer available as equivalent metrics can be obtained 
via the use of a notification handler's ``notifySend()`` method,
and filtering the calls:

- message count: count only when stage = 'pre'
- delivery count: count only when stage = 'in'


