
.. _label-trans_arg1_to_kwargs:

Transition from Arg1 to Kwargs
===============================

This section describes how to transition an application from using PyPubSub's
*arg1* messaging protocol to using the *kwargs* protocol. It proposes
some steps that will make such transition easier. These are suggestions that
have worked for some people, and any feedback would be useful.

Real example transition data: 50 listeners, 60 topics, spread out over
5000 lines of code; required one hour of manual labor (for steps 1 to 4 in 
next subsection).

To verify which messaging protocol your application uses, get the return value 
of pub.getMsgProtocol(). If it is arg1, follow the suggested steps. If it is 
kwargs, there is nothing
else to do: you are already there! For any other value, post to the PyPubSub
help forum (see URL on Installation/Support page). 

   
Suggested steps
----------------

The first step assumes that the application can run before the step is executed. 
Each subsequent step assumes that the previous step resulted in a runnable application. 
If this assumption is wrong, the step will likely fail. 

Pubsub provides some utility functions and settings that assist in the migration. 

Note that only a subset of the steps involve changing your code.  

The objective is to go from *arg1* messaging protocol, which supports ::

    pub.sendMessage('topic1')
    pub.sendMessage('topic2', yourData)

where

* ``yourData`` is your data object
* listeners must have one required parameter whose name doesn't matter
  to pubsub, ie ``listener(anyParamName)``
* listeners access the message data (``yourData``) via ``anyParamName.data``

to the *kwargs* messaging protocol, which supports ::

    pub.sendMessage('topic1')
    pub.sendMessage('topic2', argName=data)

where

* listeners of *topic1* and *topic2* MUST be of the form::

    listener()                   # for topic1
    listener(argName[=anything]) # for topic2

* listeners access the data directly (one or more argName's)


Step 1: You can do it
^^^^^^^^^^^^^^^^^^^^^^

Go to step 2. Should be simple :)

Step 2: Homogenization
^^^^^^^^^^^^^^^^^^^^^^^

Second step is to change all the listeners to take one required
parameter of the same name. This can be adjusted later but for
now this will help catch errors.

Actions for step 2:

5.  **CHOOSE** one argument name that all listeners will use. The name cannot
    be ``data`` as it is already used in ``sendMessage()``. For instance,
    ``msg``.  This is a temporary measure, so something unique (ie, easy to
    search for) is sufficient. The remainder assumes you chose ``msg``.

6. **REPLACE** the line ::

     pubsubconf.setMsgProtocol( 'arg1' )

   by the line ::

     pubsubconf.transitionV1ToV3( 'yourSelectedParamName' )

7.  **CHANGE** the first argument of all your listeners to what you chose in
    previous step, 'yourSelectedParamName'.
    
    - You can probably locate all listeners by doing a *keyword search in 
      files* for the string ``subscribe(``.
    - Don't forget to make the associated adjustments in the code of each
      listener that needs changing. You only need to change the first
      parameter name, not the ``.data`` attribute.

8.  **RUN** your application, and correct any errors: 

    - in your listeners implementation, from having forgotten to rename
      any code that access the message parameter to use the new argument name
    - If you have forgotten to fix any listeners, you will get
      ``pub.ListenerMismatchError`` exceptions at subscription time.

    **REPEAT** this step until there are no more errors. 

.. note::
    If your application runs without a console window and you don't
    catch ListenerMismatchError somewhere in your main, you may not
    have time to see the exception traceback that the Python interpreter
    prints at exit. Start your GUI app from a console, or have a catch-Exception
    or catch-ListenerMismatchError and print the error in your GUI.


Step 3: keyword arguments in sendMessage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Third step is to add a keyword argument name in ALL your calls to
``pub.sendMessage()``, and up the transition stage in
``pubsubconf.transitionV1ToV3()`` so that pubsub knows that you
want it to check that all message sending will use a keyword argument::

    pubsubconf.transitionV1ToV3( 'yourSelectedParamName', step=2 )

Actions for step 3:

9.  **ADD** the 'yourSelectedParamName' keyword name to every
    ``pub.sendMessage()`` that sends data with the message. Don't forget to
    do this in your unit tests as well. So each of your sendMessage
    should be of the form::

        pub.sendMessage('topic', yourSelectedParamName=data)

10. **REMOVE** the message parameter of any *all-topics* listeners since
    ALL_TOPICS listeners cannot get any data (except a :class:`pub.Topic``
    or via ``**kwargs``).
    Such listeners were subscribed as ``pub.subscribe(listener)``
    or ``pub.subscribe(listener, pub.ALL_TOPICS)`` instead of the typical
    ``pub.subscribe(listener, topic)``. For those listeners that really
    need the data, you can bypass pubsub's default behavior by using
    ``**kwargs`` as the message parameter, and access the data in your listener
    via ``kwargs[yourSelectedParamName].data``.
    
11. **CHANGE** the ``transitionV1ToV3`` call to be
    ``pubsubconf.transitionV1ToV3('msg', step=2)``.
    This will change the requirements imposed on listeners: in pubsub 3, 
    listeners can have any signature: regular parameters, keyword arguments, 
    and ``*args`` and ``**kwargs``. 
    
12. **RUN** your application, and correct any errors: the only ones should be
    listeners or sendMessage() calls that you forgot to adjust as per 
    steps 9 and 10. 
    
.. note::
    - Here you may get a couple different exceptions if you used the wrong
      name (not same as you gave to transitionV1ToV3), but since you already
      dealt with exceptions in phase 1, you will just see those errors in
      a console or your GUI.
    - if you get an exception raised regarding *unexpected keyword argument
      'msg'*, you probably forgot step 9;
    - if you get an exception about a sendMessage *takes exactly 2 arguments
      (3 given)*, you probably forgot to change the sendMessage() call listed
      at the bottom of the traceback.


Step 4: Remove .data
^^^^^^^^^^^^^^^^^^^^^

In this step you will remove the '.data' that appears in all listeners since
that the next configuration setting gives the data directly to your listeners:

13. **REMOVE** the '.data' wherever it is used, in all listeners

14. **REMOVE** the listener parameter for those listeners for which you
    (could) use ``pub.sendMessage('topic')``.

15. **REMOVE** the two lines involving pubsubconf (the import and the
    call to ``transitionV1ToV3()``
    
16. **RUN** your application, and correct any errors related to step 13
    

Optional steps for more Pythonesque code
----------------------------------------

After step 4, you have a topic tree in which each topic has the same
topic message specification (TMS): one argument (*yourSelectedParamName*), optional.
You can see this by adding the following lines somewhere in your application, 
after all your subscriptions have been executed::

    print pub.exportMyTopicTree()
    
The main shortcoming of your topic tree so far is that listeners 
can get any data via their *msg* argument, making it easy to send 
the wrong data to a listener. It is best to 'divide' your data
into pieces that are specific to each topic, as you would if you 
had used pubsub version 3 from the start. 

See the file :file:`tests/trans1to3/test_trans_step_5.py` from source
distribution for example of such steps.

Step 5 (optional): Split data between different arguments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To take full advantage of pubsub3, you should now split your listener 
argument (*msg*) into one or more arguments. It will be handy to refer 
to your topic tree printout for convenience.
    
1.  **SELECT** a leaf topic (one that doesn't have subtopics), and determine
    how the data currently given in associated ``sendMessage()`` calls could 
    be divided among several keyword arguments. You may want to split off 
    just one piece of data: for instance, if data was a pair (a,b) and b is
    only used by leaf topic, then split off b, as shown in the next step. 
   
2.  **ADD** relevant arguments to all ``sendMessage()`` for topic just affected. 
    For instance, 
    
      sendMessage('topicA', msg=(a,b))      # OLD
      sendMessage('topicA', msg=(a,), b=b)  # NEW
    
3.  **ADD** those arguments to all listeners of the selected topic. Make 
    the necessary adjustements to each listener's code. Leave other 
    topic listeners unchanged::
    
      # OLD:
      def listenerA(msg=None):
          ...use msg[0] and msg[1]...
      
      # NEW:
      def listenerA(msg=None, b=None):
          ...use msg[0] and b...

4.  **RUN** your application and correct any errors resulting from above 
    changes.
    
5.  **REPEAT** from 16 until satisfied, first with other leaf topics, then 
    making your way up the tree of topics, until your *msg* arguments are 
    unused in the listeners' code. 
    
6.  **REMOVE** all the unused ``msg`` arguments. 

7.  **REMOVE** default values from arguments that are *required* data. Note 
    that all listeners of the associate topic must have the same argument 
    names for both required and optional arguments. For instance to indicate 
    that *a* is required::

      # OLD:
      def listenerA1(a=None, b=None) # both a and b are optional
      def listenerA2(a=None, b=None) # both a and b are optional

      # NEW:
      def listenerA1(a, b=None)      # only b is optional
      def listenerA2(a, b=None)      # must be same signature as listenerA1


Step 6 (optional): topic tree specification
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The previous stage allows you to make it clear, on both the sending and 
receiving ends, what data is being sent with each message. However, thus
far, you have left it up to pubsub3 to infer the TMS from the first listener
subscribed. It is best to specify this explicitly, and to document your
topics. 
 
8.  **ADD** a line, for printing the topic tree definition, for instance
    ``pub.exportMyTopicTree('MyTopicTree')``

9.  **RUN** your application so all the listeners get subscribed, and exit. 

10. **EDIT** ``MyTopicTree.py``:

    - add a doc string to each topic class
    - replace the string for each arg with appropriate description
    - specify which arguments are required 
    
11. **ADD** the following at the beginning of your application::

      from MyTopicTree import MyTopicTree
      pub.importMyTopicTree( 'MyTopicTree' )
    
12. **RUN** your application again. Correct errors, mostly related to 
    some listeners no longer satisfying the TMAS for the topic they are 
    subscribing to. 
    
13. **ADD** a call to ``pub.setTopicUnspecifiedFatal()`` so that 
    TMAS inference is turned off. This will cause subscription/sendMessage
    calls for a topic that is not specified
    in MyTopicTree to raise an exception.
