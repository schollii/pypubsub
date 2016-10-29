"""
The fift step consists in two activities: 

- rename message data arguments to be representative of the
  data carried, and
- break up the message over several keyword arguments, where relevant.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from nose.tools import assert_raises

from pubsub import pub


# ---------------------------------

def listenerAll(**kwargs):
    pass

def listener1():
    pass

def listener1_1(number):
    assert number == 123

def listener2(item1):
    assert item1 == 'abc'

def listener2_1(item1, item2):
    assert item1 == 'abc'
    assert item2 == 456

# pretend you forgot to change the parameter name for this listener:
def listenerForget(msg):
    pass

def listenerForget2(item1=None):
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
    pub.sendMessage('t1.s1', number = 123 )
    pub.sendMessage('t2',    item1 = 'abc' )
    pub.sendMessage('t2.s2', item1 = 'abc', item2 = 456)

    assert_raises(pub.ListenerMismatchError, pub.subscribe, listenerForget, 't1.s1')
    pub.subscribe(listenerForget2, 't2')

    