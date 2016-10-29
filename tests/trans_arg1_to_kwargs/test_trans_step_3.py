"""
Third step is to add a keyword argument name in ALL your calls to
sendMessage(), and up the transition stage so pubsub knows that you
want it to check that all message sending will use a keyword argument::

    from pubsub import setupkwargs
    setupkwargs.transitionFromArg1('msg')

Each of your sendMessage should be of the form::

    pub.sendMessage('topic', yourSelectedParamName=data)

Here you may get a couple different exceptions if you used the wrong
name (not same as you gave to enforceArgName), but since you already
dealt with exceptions in phase 1, you will just see those errors in
a console or your GUI.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from nose.tools import assert_raises

from pubsub import setupkwargs
setupkwargs.transitionFromArg1('msg')

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

def listenerAll(): 
    pass

def listener1(msg):
    assert msg.data in ( None, 123 )
    assert str(msg).startswith('[Topic')

def listener1_1(msg):
    assert msg.data == 123

def listener2(msg):
    assert msg.data.item1 == 'abc'

def listener2_1(msg):
    assert msg.data.item1 == 'abc'
    assert msg.data.item2 == 456

# pretend you forgot to change the parameter name for this listener:
def listenerForget(msg):
    pass

def listenerForget2(msg=None):
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
    pub.sendMessage('t1.s1', msg = 123 )
    pub.sendMessage('t2',    msg = MsgData1('abc') )
    pub.sendMessage('t2.s2', msg = MsgData2('abc', 456) )

    pub.subscribe(listenerForget, 't1.s1')
    pub.subscribe(listenerForget2, 't2')
    
    assert_raises(RuntimeError, pub.sendMessage, 't1.s1', nonMsg=123 )
    assert_raises(RuntimeError, pub.sendMessage, 't2', msg=123, nonMsg=456 )
    
    