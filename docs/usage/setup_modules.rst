Setup Modules
========================

There are two setup modules for pubsub; only one can be imported in an application. 


pubsub.setupkwargs
--------------------------

.. automodule:: pubsub.setupkwargs

The *kwargs* protocol is defined as follows:

- the sender provides message data via keyword (i.e. named) arguments. The keywords
  must be the same for all messages of the same topic. 

- the listener must be callable as ``listener(*req_data, **opt_data)``: the 
  parameter names must be the same for all listeners of a topic, and must be 
  the same as the message data items. 
  
Example::

    from pubsub import pub
    
    def listener1(msg):
        assert msg == 'hi'
        
    def listener(r1, o1=None): 
        assert r1 == 123
        assert o1 is None
    
    pub.subscribe(listener1, 'someTopic_1')
    pub.subscribe(listener2, 'someTopic_2')
    
    pub.sendMessage('someTopic_1', msg='hi')
    pub.sendMessage('someTopic_2', r1=123) # ok: o1 optional


.. autofunction:: pubsub.setupkwargs.transitionFromArg1


pubsub.setuparg1
------------------------

.. automodule:: pubsub.setuparg1

The *arg1* protocol is defined as follows:

- the sender only provides one data, or nothing. This one data can be any object: 
  a string, a tuple, a dictionary, etc. 

- the listener must be callable as ``listener(message)``: the message.data 
  is the data given by the sender. The message contains other information such as
  topic. 
  
An important consequence of the freedom of this protocol is that the same listener
can subscribe to any topic; it is the listener's responsibility to determine what 
data is packaged in message.data and use properly. 

Example::

    from pubsub import setuparg1
    from pubsub import pub
    
    def listener1(msg):
        assert msg.data == 'hi'
    
    def listener2(msg): 
        assert msg.data['r1'] == 123
    
    pub.subscribe(listener1, 'someTopic')
    pub.subscribe(listener2, 'someTopic') # same topic ok despite differing message data
    
    pub.sendMessage('someTopic', 'hi')
    
    data = {'r1':123, ...} # replace ... with whatever you want
    pub.sendMessage('someTopic', data)

.. autofunction:: pubsub.setuparg1.enforceArgName

