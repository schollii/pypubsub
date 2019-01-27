"""
Except for one test, this file tests with auto-creation of topics
disabled, as it is more rigorous for testing purposes.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import gc

import pytest

import pubsub.core.topicargspec
from pubsub import pub
from pubsub.utils.notification import IgnoreNotificationsMixin
from pubsub.core import getListenerID, ListenerMismatchError

topicMgr = pub.getDefaultTopicMgr()


def testDOAListenerPubsub():
    # Verify that a 'temporary' listener (one that will be garbage collected
    # as soon as subscribe() returns because there are no strong references to
    # it) gets immediately unregistered

    def listener(): pass
    class Wrapper:
        def __init__(self, func):
            self.func = func
        def __call__(self):
            pass

    pub.subscribe( Wrapper(listener), 'testDOAListenerPubsub')
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert not topicMgr.getTopic('testDOAListenerPubsub').hasListeners()
    assert pub.isValid(listener, 'testDOAListenerPubsub')


def testDeadListener():
    # create a listener for listeners that have died
    class DeathListener(IgnoreNotificationsMixin):
        listenerStr = ''
        def notifyDeadListener(self, pubListener, topicObj):
            assert topicObj.getName() == 'sadTopic'
            #import pdb; pdb.set_trace()
            #print 'hi again'
            DeathListener.listenerStr = pubListener.name()
    dl = DeathListener()
    pub.addNotificationHandler( dl )
    pub.setNotificationFlags(deadListener=True)

    # define a topic, subscribe to it, and kill its listener:
    class TempListener:
        def __call__(self, **kwargs):
            pass
        def __del__(self):
            # print 'being deleted'
            pass
    #def tempListener(): pass
    tempListener = TempListener()
    expectLisrStr, _ = getListenerID(tempListener)
    pub.subscribe(tempListener, 'sadTopic')
    del tempListener

    # verify:
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert DeathListener.listenerStr.startswith(expectLisrStr), \
        '"%s" !~ "%s"' % (DeathListener.listenerStr, expectLisrStr)

    pub.addNotificationHandler(None)
    pub.clearNotificationHandlers()


def testSubscribe():
    topicName = 'testSubscribe'
    def proto(a, b, c=None): pass
    topicMgr.getOrCreateTopic(topicName, proto)

    def listener(a, b, c=None): pass
    # verify that pub.isValid() works too
    pub.validate(listener, topicName)
    assert pub.isValid(listener, topicName)

    assert topicMgr.getTopic(topicName).getNumListeners() == 0
    assert topicMgr.getTopicsSubscribed(listener) == []
    assert not pub.isSubscribed(listener, topicName)
    assert pub.subscribe(listener, topicName)
    assert pub.isSubscribed(listener, topicName)
    def topicNames(listener):
        return [t.getName() for t in topicMgr.getTopicsSubscribed(listener)]
    assert topicNames(listener) == [topicName]
    # should do nothing if already subscribed:
    assert not pub.subscribe(listener, topicName)[1]
    assert topicMgr.getTopic(topicName).getNumListeners() == 1

    # test topicMgr.getTopicsSubscribed()
    pub.subscribe(listener, 'lt2', )
    assert set(topicNames(listener)) == set([topicName,'lt2'])
    pub.subscribe(listener, 'lt1.lst1')
    assert set(topicNames(listener)) == set([topicName,'lt2','lt1.lst1'])

    # test ALL_TOPICS
    def listenToAll(): pass
    pub.subscribe(listenToAll, pub.ALL_TOPICS)
    assert topicNames(listenToAll) == [pub.ALL_TOPICS]

    # test type hints in listeners:
    def listenerWithHints(a: int, b: bool, c: str = 2): pass
    topicForHintedListeners = 'topicForHints'
    topicMgr.getOrCreateTopic(topicForHintedListeners, listenerWithHints)
    assert not pub.isSubscribed(listenerWithHints, topicForHintedListeners)
    pub.subscribe(listenerWithHints, topicForHintedListeners)
    assert pub.subscribe(listenerWithHints, topicForHintedListeners)
    assert pub.isSubscribed(listenerWithHints, topicForHintedListeners)


def testMissingReqdArgs():
    def proto(a, b, c=None): pass
    topicMgr.getOrCreateTopic('missingReqdArgs', proto)
    pytest.raises(pubsub.core.topicargspec.SenderMissingReqdMsgDataError, pub.sendMessage, 'missingReqdArgs', a=1)


def testSendTopicWithMessage():
    class MyListener:
        def __init__(self):
            self.count = 0
            self.heardTopic = False
            self.listen2Topics = []
        def listen0(self):
            pass
        def listen1(self, **kwarg):
            self.count += 1
            self.heardTopic = True
        def listen2(self, msgTopic=pub.AUTO_TOPIC, **kwarg):
            self.listen2Topics.append(msgTopic.getName())

    my = MyListener()
    pub.subscribe(my.listen0, 'testSendTopic')
    pub.subscribe(my.listen1, 'testSendTopic')
    pub.subscribe(my.listen2, 'testSendTopic')

    pub.sendMessage('testSendTopic')
    assert my.count == 1
    assert my.heardTopic == True

    pub.subscribe(my.listen0, 'testSendTopic.subtopic')
    pub.subscribe(my.listen1, 'testSendTopic.subtopic')
    pub.subscribe(my.listen2, 'testSendTopic.subtopic')

    pub.sendMessage('testSendTopic.subtopic')
    assert my.count == 3
    assert [] == [topic for topic in my.listen2Topics
        if topic not in ('testSendTopic', 'testSendTopic.subtopic')]

    # type hints on listeners:
    result = []
    def listenerWithHints(a: int, b: bool, c: str = 2): result.append((a, b, c))
    topicForHintedListeners = 'topicForHints'
    pub.subscribe(listenerWithHints, topicForHintedListeners)
    assert pub.subscribe(listenerWithHints, topicForHintedListeners)
    pub.sendMessage(topicForHintedListeners, b=456, a=123, c='hello')
    assert result == [(123, 456, 'hello')]


def testOptionalArgs():
    # first function registered determines topic MDS (message data spec)
    # here we first register a more "permissive" listener, ie one that has default values for args
    # that the second listener does not; therefore pubsub should refuse subscribing second listener
    # to same topic

    def myFunction1(arg1, arg2=2, *, kwarg1, kwarg2=4, **kwargs): pass
    def myFunction2(arg1, arg2,   *, kwarg1, kwarg2=4, **kwargs): pass

    pub.subscribe(myFunction1, 'testKeywordOnlyArgs')
    pytest.raises(ListenerMismatchError, pub.subscribe, myFunction2, 'testKeywordOnlyArgs')


def testKeywordOnlyArgsStar():
    def capture(funcName, *args):
        result[funcName] = args

    def myFunction1(arg1, arg2, *, kwarg1, kwarg2=4, **kwargs):
        capture('myFunction1', arg1, arg2, kwarg1, kwarg2, kwargs)

    def myFunction2(arg1, arg2, *arg3, kwarg1, kwarg2=4, **kwargs):
        capture('myFunction2', arg1, arg2, arg3, kwarg1, kwarg2, kwargs)

    pub.subscribe(myFunction1, 'testKeywordOnlyArgsStar')
    pub.subscribe(myFunction2, 'testKeywordOnlyArgsStar')

    result = {}
    pub.sendMessage('testKeywordOnlyArgsStar', arg1=1, arg2=2, kwarg1=3)
    assert result == dict(myFunction1=(1, 2, 3, 4, {}), myFunction2=(1, 2, (), 3, 4, {}))


def testKeywordOnlyArgsStarAfterOpt():
    def capture(funcName, *args):
        result[funcName] = args

    def myFunction1(arg1, arg2=2, *, kwarg1, kwarg2=4, **kwargs):
        capture('myFunction1', arg1, arg2, kwarg1, kwarg2, kwargs)
    def myFunction2(arg1, arg2=2, *arg3, kwarg1, kwarg2=4, **kwargs):
        capture('myFunction2', arg1, arg2, arg3, kwarg1, kwarg2, kwargs)

    pub.subscribe(myFunction1, 'testKeywordOnlyArgsStarAfterOpt')
    pub.subscribe(myFunction2, 'testKeywordOnlyArgsStarAfterOpt')

    result = dict()
    pub.sendMessage('testKeywordOnlyArgsStarAfterOpt', arg1=1, kwarg1=3)
    assert result == dict(myFunction1=(1, 2, 3, 4, {}), myFunction2=(1, 2, (), 3, 4, {}))


def testKeywordOnlyArgsNoDefaults():
    def capture(funcName, *args):
        result[funcName] = args

    def myFunction1(*, kwarg1, kwarg2): capture('myFunction1', kwarg1, kwarg2)
    def myFunction2(*args, kwarg1, kwarg2): capture('myFunction2', args, kwarg1, kwarg2)
    def myFunction3(*, kwarg1, kwarg2, **kwargs): capture('myFunction3', kwarg1, kwarg2, kwargs)
    def myFunction4(*args, kwarg1, kwarg2, **kwargs): capture('myFunction4', args, kwarg1, kwarg2, kwargs)

    pub.subscribe(myFunction1, 'testKeywordOnlyArgsNoDefaults')
    pub.subscribe(myFunction2, 'testKeywordOnlyArgsNoDefaults')
    pub.subscribe(myFunction3, 'testKeywordOnlyArgsNoDefaults')
    pub.subscribe(myFunction4, 'testKeywordOnlyArgsNoDefaults')

    result = {}
    pub.sendMessage('testKeywordOnlyArgsNoDefaults', kwarg1=1, kwarg2=2)
    assert result == dict(myFunction1=(1, 2), myFunction2=((), 1, 2), myFunction3=(1, 2, {}), myFunction4=((), 1, 2, {}))


def testAcceptAllArgs():
    def listen(arg1=None): pass
    def listenAllArgs(arg1=None, **kwargs): pass
    def listenAllArgs2(arg1=None, msgTopic=pub.AUTO_TOPIC, **kwargs): pass

    pub.subscribe(listen,  'testAcceptAllArgs')

    pub.subscribe(listenAllArgs,  'testAcceptAllArgs')
    pub.subscribe(listenAllArgs2, 'testAcceptAllArgs')

    pub.subscribe(listenAllArgs2, 'testAcceptAllArgs.subtopic')
    pub.subscribe(listenAllArgs,  'testAcceptAllArgs.subtopic')


def testSubscribeCurriedListeners():
    result = []

    def proto_listener(a, b, c=1, d=2):
        pass
    def listener1(a, b, c=1, d=2, nonTopicArg=3):
        result.append((a, b, c, d))

    # no currying:
    pub.subscribe(proto_listener, 'topic1')
    pub.subscribe(listener1, 'topic1')

    # ok:
    pub.subscribe(proto_listener, 'topic2')
    pub.subscribe(listener1, 'topic2', nonTopicArg=4)

    # curried arg typo:
    pub.subscribe(proto_listener, 'topic3')
    pytest.raises(ListenerMismatchError, pub.subscribe, listener1, 'topic3', invalidArg=4)

    # curried arg is in topic args:
    pub.subscribe(proto_listener, 'topic4')
    pytest.raises(ListenerMismatchError, pub.subscribe, listener1, 'topic4', a=4)


def testSendWhenCurriedArgs():
    result = []
    def listen(a, b, c, d=0, e=0):
        result.append((a, b, c, d, e))

    wrapped = pub.subscribe(listen, 'testCurriedArgs', b=2, d=4)
    assert wrapped[0].curriedArgs
    pub.sendMessage('testCurriedArgs', a=1, c=3)
    assert result[0] == (1, 2, 3, 4, 0)


def testUnsubAll():
    def lisnr1(): pass
    def lisnr2(): pass
    class MyListener:
        def __call__(self): pass
        def meth(self): pass
        def __hash__(self): return 123
    lisnr3 = MyListener()
    lisnr4 = lisnr3.meth
    def lisnrSub(listener=None, topic=None, newSub=None): pass
    pub.subscribe(lisnrSub, 'pubsub.subscribe')
    assert topicMgr.getTopic('pubsub.subscribe').getNumListeners() == 1

    def subAll():
        pub.subscribe(lisnr1, 'testUnsubAll')
        pub.subscribe(lisnr2, 'testUnsubAll')
        pub.subscribe(lisnr3, 'testUnsubAll')
        pub.subscribe(lisnr4, 'testUnsubAll')
        assert topicMgr.getTopic('testUnsubAll').getNumListeners() == 4

    def filter(lisnr):
        passes = str(lisnr).endswith('meth')
        return passes

    # test unsub many non-pubsub topic listeners
    subAll()
    pub.unsubAll('testUnsubAll')
    assert topicMgr.getTopic('testUnsubAll').getNumListeners() == 0
    assert topicMgr.getTopic('pubsub.subscribe').getNumListeners() == 1
    # now same but with filter:
    subAll()
    unsubed = pub.unsubAll('testUnsubAll', listenerFilter=filter)
    assert topicMgr.getTopic('testUnsubAll').getNumListeners() == 3
    assert topicMgr.getTopic('pubsub.subscribe').getNumListeners() == 1

    # test unsub all listeners of all topics
    subAll()
    assert topicMgr.getTopic('testUnsubAll').getNumListeners() == 4
    unsubed = pub.unsubAll(listenerFilter=filter)
    assert unsubed == [lisnr4]
    assert topicMgr.getTopic('testUnsubAll').getNumListeners() == 3
    assert topicMgr.getTopic('pubsub.subscribe').getNumListeners() == 1
    unsubed = set( pub.unsubAll() )
    expect = set([lisnr1, lisnrSub, lisnr3, lisnr2])
    # at least all the 'expected' ones were unsub'd; will be others if this
    # test is run after other unit tests in same py.test run
    assert unsubed >= expect


def testSendForUndefinedTopic():
    pub.sendMessage('testSendForUndefinedTopic')
    assert topicMgr.getTopic('testSendForUndefinedTopic')
    assert topicMgr.getTopic('testSendForUndefinedTopic').getArgs() == (None, None)

    # must also check for subtopics if parents have listeners since
    # filtering of args is affected
    def listener(): pass
    pub.subscribe(listener, 'testSendForUndefinedTopic')
    pub.sendMessage('testSendForUndefinedTopic.subtopic', msg='something')

def testTopicUnspecifiedError():
    pytest.raises(pub.TopicDefnError, pub.setTopicUnspecifiedFatal)
    pub.setTopicUnspecifiedFatal(checkExisting=False)
    def fn(): pass
    LSI = pub.TopicDefnError
    pytest.raises(LSI, pub.sendMessage, 'testTopicUnspecifiedError')
    pytest.raises(LSI, pub.subscribe, fn, 'testTopicUnspecifiedError')
    pub.setTopicUnspecifiedFatal(False)
    pub.sendMessage('testTopicUnspecifiedError')
    pub.subscribe(fn, 'testTopicUnspecifiedError')


def testArgSpecDerivation():
    def ok_0(): pass

    def ok_1(arg1): pass
    def err_11(arg1=None): pass  # required can't become optional!
    def err_12(arg2): pass       # parent's arg1 missing

    def ok_2(arg1=None): pass
    def ok_21(arg1): pass        # optional can become required
    def err_22(arg2): pass       # parent's arg1 missing

    # with getOrCreateTopic(topic, proto), the 'required args' set
    # is garanteed to be a subset of 'all args'
    topicMgr.getOrCreateTopic('tasd',          ok_0)
    topicMgr.getOrCreateTopic('tasd.t_1',      ok_1)
    pytest.raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_1.t_11',  err_11)
    pytest.raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_1.t_12',  err_12)
    topicMgr.getOrCreateTopic('tasd.t_2',      ok_2)
    topicMgr.getOrCreateTopic('tasd.t_2.t_21', ok_21)
    pytest.raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_2.t_22', err_22)

    print()


def testListenerChangesListenerList():
    """pubsub supports un/subscribing of listeners while sendMessage
    in progress. This requires that the TopicManager instance
    properly loop over listeners, via a copy of list instead of
    iterator on list (since lists can't be modified while iteration
    in progress. This test verifies that listener receiving message
    can subscribe another listener to same topic, and can unsubscribe
    self while handling message. """

    class Listeners:
        callCountForNewListener = 0
        callCountForChanger = 0

        def newListener(self):
            self.callCountForNewListener += 1
            pub.unsubscribe(self.newListener, 'test.change-listeners')

        def changer(self):
            # first time, subscribe new listener; if don't have this, will fail in
            # py3 because order of listeners opposite, so unsub will happen before
            # the sub (which succeeds even if no listeners) and newListener will
            # remain subscribed.
            if self.callCountForChanger == 0:
                pub.subscribe(self.newListener, 'test.change-listeners')
            self.callCountForChanger += 1

    testListeners = Listeners()
    pub.subscribe(testListeners.changer, 'test.change-listeners')
    topic = pub.getDefaultTopicMgr().getTopic('test.change-listeners')

    pub.sendMessage('test.change-listeners')
    assert testListeners.callCountForChanger ==     1
    assert testListeners.callCountForNewListener == 0
    assert topic.getNumListeners() == 2

    pub.sendMessage('test.change-listeners')
    assert testListeners.callCountForChanger ==     2
    assert testListeners.callCountForNewListener == 1
    assert topic.getNumListeners() == 1

    pub.sendMessage('test.change-listeners')
    assert testListeners.callCountForChanger ==     3
    assert testListeners.callCountForNewListener == 1
