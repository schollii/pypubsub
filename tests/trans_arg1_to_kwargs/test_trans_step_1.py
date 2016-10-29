"""
There are essentially 5 things to do for this transition.
In a larger application with lots of topics, listeners and senders,
doing this transition ad-hoc will likely introduce many errors at
application runtime. A 5-step systematic approach is supported by pubsub
that isolates each of the five actions so that only certain types of
problems have to be corrected at each step.

Explanations are provided in the API documentation section
:ref:`label-trans_arg1_to_kwargs`.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from pubsub import setuparg1
from pubsub import pub


# ---------------------------------

class MsgData1:
    def __init__(self, item1):
        self.item1 = item1

class MsgData2:
    def __init__(self, item1, item2):
        self.item1 = item1
        self.item2 = item2


# ---------------------------------

def listenerAll(*unused):
    assert unused is not None
    
def listener1(msg):
    assert msg.data in ( None, 123 )
    assert str(msg).startswith('[Topic')
    
def listener1_1(number):
    assert number.data == 123
    
def listener2(arg):
    assert isinstance(arg.data, MsgData1) or isinstance(arg.data, MsgData2)
    assert arg.data.item1 == 'abc'
    
def listener2_1(arg):
    assert isinstance(arg.data, MsgData2)
    assert arg.data.item1 == 'abc'
    assert arg.data.item2 == 456
    
def listenerForget(nonMsg):
    pass

def listenerForget2(nonMsg=None):
    pass


# ---------------------------------

def testTransition():
    # subscribe; this will created any topics not already defined
    pub.subscribe(listenerAll, pub.ALL_TOPICS)
    pub.subscribe(listener1,   't1')
    pub.subscribe(listener1_1, 't1.s1')
    pub.subscribe(listener2,   't2')
    pub.subscribe(listener2_1, 't2.s2')

    # send some more messages
    pub.sendMessage('t1' )
    pub.sendMessage('t1.s1', 123 )
    pub.sendMessage('t2',    MsgData1('abc') )
    pub.sendMessage('t2.s2', MsgData2('abc', 456) )
    
    pub.subscribe(listenerForget, 't1.s1')
    pub.subscribe(listenerForget2, 't2')
    
    