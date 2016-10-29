"""
Second step is to change all the listeners to take one required
parameter of the same name. This can be adjusted later but for
now this will help catch errors. To do this, call::

    from pubsub import setuparg1
    setuparg1.enforceArgName('msg')

and change all your listeners to have one required parameter named
'yourSelectedParamName'. Run your application and test. If you have
forgotten to fix any listeners, you will get ListenerMismatchError
exceptions at subscription time.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from nose.tools import assert_raises

from pubsub import setuparg1
setuparg1.enforceArgName('msg')

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

def listener1_1(msg):
    assert msg.data == 123

def listener2(msg):
    assert msg.data.item1 == 'abc'

def listener2_1(msg):
    assert msg.data.item1 == 'abc'
    assert msg.data.item2 == 456

# pretend you forgot to change the parameter name for this listener:
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

    # attempt to subscribe listenerForgets should raise exception:
    assert_raises(pub.ListenerMismatchError, pub.subscribe, listenerForget, 't1.s1')
    assert_raises(pub.ListenerMismatchError, pub.subscribe, listenerForget2, 't2')
    