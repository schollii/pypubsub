"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import pytest

from pubsub.core.topicobj     import Topic
from pubsub.core.topicmgr     import TreeConfig
from pubsub.core.topicutils   import ALL_TOPICS
from pubsub.core.topicargspec import ArgsInfo, ArgSpecGiven
from pubsub.core.listener     import ListenerMismatchError
from pubsub.core.topicexc     import MessageDataSpecError



rootTopic = None
treeConfig = TreeConfig()


def test_CreateRoot():
    #
    # Test create and then modify state of a topic object
    #

    nameTuple = ('root',)
    description = 'root description'
    msgArgsInfo = None

    # when parent is None, only nameTuple=ALL_TOPICS is allowed, thereby
    # guaranteeing that only one tree root can be created
    pytest.raises(ValueError, Topic, treeConfig, nameTuple, description, msgArgsInfo)

    # create the ALL TOPICS topic; it has no message args
    nameTuple = (ALL_TOPICS,)
    argSpec = ArgSpecGiven( dict() )
    msgArgsInfo = ArgsInfo(nameTuple, argSpec, None)
    obj = Topic(treeConfig, nameTuple, description, msgArgsInfo)

    # verify its state is as expected after creation:
    assert obj.getListeners() == []
    assert obj.getNumListeners() == 0
    assert obj.hasListeners() == False

    def listener1(): pass
    def listener2(): pass
    def badListener1(arg1): pass # extra required arg
    def listener3(arg1=None): pass # extra is optional
    assert obj.isValid(listener1)
    assert not obj.isValid(badListener1)
    assert obj.isValid(listener3)

    global rootTopic
    rootTopic = obj


def test_SubUnsub():
    #
    # Test subscription and unsubscription of listeners
    #

    def listener1(): pass
    def listener2(): pass
    obj = rootTopic

    # now modify its state by subscribing listeners
    obj.subscribe(listener1)
    obj.subscribe(listener2)

    obj.hasListener(listener1)
    obj.hasListener(listener2)
    assert obj.hasListeners() == True
    assert set(obj.getListenersIter()) == set([listener1, listener2])
    assert obj.getNumListeners() == 2

    # try to subscribe an invalid listener
    def badListener(arg1): pass # extra required arg
    pytest.raises(ListenerMismatchError, obj.subscribe, badListener)

    # try unsubscribe
    obj.unsubscribe(listener1)
    assert obj.hasListeners()
    assert obj.getListeners() == [listener2]
    assert obj.getNumListeners() == 1

    # try unsubscribe all, with filtering
    obj.subscribe(listener1)
    def listener3(): pass
    obj.subscribe(listener3)
    assert obj.getNumListeners() == 3
    def ff(listener):
        # use != since it is defined in terms of ==; also, put listener
        # on RHS to verify works even when Listener used on RHS
        return listener2 != listener
    obj.unsubscribeAllListeners(filter=ff)
    assert obj.getNumListeners() == 1
    assert obj.getListeners() == [listener2]
    obj.subscribe(listener1)
    obj.subscribe(listener3)
    assert obj.getNumListeners() == 3
    obj.unsubscribeAllListeners()
    assert obj.getNumListeners() == 0


def test_CreateChild():
    #
    # Test creation of a child topic, subscription of listeners
    #

    nameTuple = ('childOfAll',)
    description = 'child description'
    argsDocs = dict(arg1='arg1 desc', arg2='arg2 desc')
    reqdArgs = ('arg2',)
    argSpec = ArgSpecGiven(argsDocs=argsDocs, reqdArgs = reqdArgs)
    msgArgsInfo = ArgsInfo(nameTuple, argSpec, rootTopic._getListenerSpec())
    parent = Topic(treeConfig, nameTuple, description, msgArgsInfo, parent=rootTopic)
    assert parent.getParent() is rootTopic

    # now create a child of child with wrong arguments so we can test exceptions
    nameTuple = ('childOfAll', 'grandChild')
    description = 'grandchild description'

    def tryCreate(ad, r):
        argSpec = ArgSpecGiven(argsDocs=ad, reqdArgs = r)
        msgArgsInfo = ArgsInfo(nameTuple, argSpec, parent._getListenerSpec())
        obj = Topic(treeConfig, nameTuple, description, msgArgsInfo, parent=parent)

    # test when all OK
    argsDocs = dict(arg1='arg1 desc', arg2='arg2 desc')
    reqdArgs = ('arg2',)
    tryCreate(argsDocs, reqdArgs)
    # test when requiredArg wrong
    reqdArgs = ('arg3',)
    pytest.raises(MessageDataSpecError, tryCreate, argsDocs, reqdArgs)
    reqdArgs = ()
    pytest.raises(MessageDataSpecError, tryCreate, argsDocs, reqdArgs)
    # test when missing opt arg
    argsDocs = dict(arg1='arg1 desc', arg2='arg2 desc')
    reqdArgs = ('arg2',)

