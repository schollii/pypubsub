"""
In the fourth, you do two things:

- remove the .data attribute used in all listeners
- remove the listener parameter for those listeners for which you
  (could) use sendMessage('topic').

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from nose.tools import assert_raises

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

def listenerAll(**kwargs):
    pass

def listener1():
    pass

def listener1_1(msg):
    assert msg == 123

def listener2(msg):
    assert msg.item1 == 'abc'

def listener2_1(msg):
    assert msg.item1 == 'abc'
    assert msg.item2 == 456

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

    