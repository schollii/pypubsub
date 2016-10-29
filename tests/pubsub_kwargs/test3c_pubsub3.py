"""
Except for one test, this file tests with auto-creation of topics 
disabled, as it is more rigorous for testing purposes. 

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import gc
from nose.tools import assert_raises, assert_equal, assert_not_equal

from pubsub import (pub, py2and3)
from pubsub.utils.notification import IgnoreNotificationsMixin
from pubsub.core import getListenerID

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
            assert_equal( topicObj.getName(), 'sadTopic' )
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

    assert_equal(topicMgr.getTopic(topicName).getNumListeners(), 0)
    assert_equal(topicMgr.getTopicsSubscribed(listener), [])
    assert not pub.isSubscribed(listener, topicName)
    assert pub.subscribe(listener, topicName)
    assert pub.isSubscribed(listener, topicName)
    def topicNames(listener):
        return [t.getName() for t in topicMgr.getTopicsSubscribed(listener)]
    assert_equal(topicNames(listener), [topicName])
    # should do nothing if already subscribed:
    assert not pub.subscribe(listener, topicName)[1]
    assert_equal(topicMgr.getTopic(topicName).getNumListeners(), 1)
    
    # test topicMgr.getTopicsSubscribed()
    pub.subscribe(listener, 'lt2', )
    assert_equal( set(topicNames(listener)), 
                  set([topicName,'lt2']))
    pub.subscribe(listener, 'lt1.lst1')
    assert_equal( set(topicNames(listener)), 
                  set([topicName,'lt2','lt1.lst1']))
    
    # test ALL_TOPICS
    def listenToAll(): pass
    pub.subscribe(listenToAll, pub.ALL_TOPICS)
    assert_equal( topicNames(listenToAll), [pub.ALL_TOPICS] )
    
    
def testMissingReqdArgs():
    def proto(a, b, c=None): pass
    topicMgr.getOrCreateTopic('missingReqdArgs', proto)
    assert_raises(pub.SenderMissingReqdMsgDataError, pub.sendMessage, 'missingReqdArgs', a=1)


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
    assert_equal( my.count, 1)
    assert_equal( my.heardTopic, True)

    pub.subscribe(my.listen0, 'testSendTopic.subtopic')
    pub.subscribe(my.listen1, 'testSendTopic.subtopic')
    pub.subscribe(my.listen2, 'testSendTopic.subtopic')

    pub.sendMessage('testSendTopic.subtopic')
    assert_equal( my.count, 3)
    assert_equal( [], [topic for topic in my.listen2Topics 
        if topic not in ('testSendTopic', 'testSendTopic.subtopic')] )


def testAcceptAllArgs():
    def listen(arg1=None): pass
    def listenAllArgs(arg1=None, **kwargs): pass
    def listenAllArgs2(arg1=None, msgTopic=pub.AUTO_TOPIC, **kwargs): pass

    pub.subscribe(listen,  'testAcceptAllArgs')

    pub.subscribe(listenAllArgs,  'testAcceptAllArgs')
    pub.subscribe(listenAllArgs2, 'testAcceptAllArgs')
    
    pub.subscribe(listenAllArgs2, 'testAcceptAllArgs.subtopic')
    pub.subscribe(listenAllArgs,  'testAcceptAllArgs.subtopic')


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
    assert_equal( topicMgr.getTopic('pubsub.subscribe').getNumListeners(), 1)

    def subAll():
        pub.subscribe(lisnr1, 'testUnsubAll')
        pub.subscribe(lisnr2, 'testUnsubAll')
        pub.subscribe(lisnr3, 'testUnsubAll')
        pub.subscribe(lisnr4, 'testUnsubAll')
        assert_equal( topicMgr.getTopic('testUnsubAll').getNumListeners(), 4 )

    def filter(lisnr):
        passes = str(lisnr).endswith('meth')
        return passes
        
    # test unsub many non-pubsub topic listeners
    subAll()
    pub.unsubAll('testUnsubAll')
    assert_equal( topicMgr.getTopic('testUnsubAll').getNumListeners(), 0 )
    assert_equal( topicMgr.getTopic('pubsub.subscribe').getNumListeners(), 1)
    # now same but with filter:
    subAll()
    unsubed = pub.unsubAll('testUnsubAll', listenerFilter=filter)
    assert_equal( topicMgr.getTopic('testUnsubAll').getNumListeners(), 3 )
    assert_equal( topicMgr.getTopic('pubsub.subscribe').getNumListeners(), 1)
    
    # test unsub all listeners of all topics
    subAll()
    assert_equal( topicMgr.getTopic('testUnsubAll').getNumListeners(), 4 )
    unsubed = pub.unsubAll(listenerFilter=filter)
    assert_equal( unsubed, [lisnr4] )
    assert_equal( topicMgr.getTopic('testUnsubAll').getNumListeners(), 3 )
    assert_equal( topicMgr.getTopic('pubsub.subscribe').getNumListeners(), 1)
    unsubed = set( pub.unsubAll() )
    expect = set([lisnr1, lisnrSub, lisnr3, lisnr2])
    # at least all the 'expected' ones were unsub'd; will be others if this
    # test is run after other unit tests in same nosetests run
    assert unsubed >= expect
    
    
def testSendForUndefinedTopic():
    pub.sendMessage('testSendForUndefinedTopic')
    assert topicMgr.getTopic('testSendForUndefinedTopic')
    assert_equal( topicMgr.getTopic('testSendForUndefinedTopic').getArgs(),
        (None, None) )

    # must also check for subtopics if parents have listeners since
    # filtering of args is affected
    def listener(): pass
    pub.subscribe(listener, 'testSendForUndefinedTopic')
    pub.sendMessage('testSendForUndefinedTopic.subtopic', msg='something')
    
def testTopicUnspecifiedError():
    assert_raises(pub.TopicDefnError, pub.setTopicUnspecifiedFatal)
    pub.setTopicUnspecifiedFatal(checkExisting=False)
    def fn(): pass
    LSI = pub.TopicDefnError
    assert_raises(LSI, pub.sendMessage, 'testTopicUnspecifiedError')
    assert_raises(LSI, pub.subscribe, fn, 'testTopicUnspecifiedError')
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
    assert_raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_1.t_11',  err_11)
    assert_raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_1.t_12',  err_12)
    topicMgr.getOrCreateTopic('tasd.t_2',      ok_2)
    topicMgr.getOrCreateTopic('tasd.t_2.t_21', ok_21)
    assert_raises( pub.MessageDataSpecError, topicMgr.getOrCreateTopic, 'tasd.t_2.t_22', err_22)

    py2and3.print_()
    
    # with newTopic(), 'required args' specified separately so
    # verify that errors caught
    def check(subName, required=(), **args):
        tName = 'tasd.'+subName
        try:
            topicMgr.newTopic(tName, 'desc', required, **args)
            msg = 'Should have raised pub.MessageDataSpecError for %s, %s, %s'
            assert False, msg % (tName, required, args)
        except pub.MessageDataSpecError:
            #import traceback
            #traceback.print_exc()
            from pubsub import py2and3
            exc = py2and3.getexcobj()
            py2and3.print_('As expected: ', exc)

    topicMgr.newTopic('tasd.t_1.t_13', 'desc', ('arg1',), arg1='docs for arg1') # ok_1
    check('t_1.t_14', arg1='docs for arg1')                                # err_11
    check('t_1.t_15', ('arg2',), arg2='docs for arg2')                     # err_12

    topicMgr.newTopic('tasd.t_2.t_23', 'desc', ('arg1',), arg1='docs for arg1') # ok_21
    check('t_2.t_24', ('arg2',), arg2='docs for arg2')                     # err_22

    # check when no inheritence involved
    # reqd args wrong
    check('t_1.t_16', ('arg1',), arg2='docs for arg2')
    check('t_1.t_17', ('arg2',), arg1='docs for arg1')
    check('t_3',      ('arg1',), arg2='docs for arg2')

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
    assert_equal(testListeners.callCountForChanger,     1)
    assert_equal(testListeners.callCountForNewListener, 0)
    assert_equal(topic.getNumListeners(), 2)

    pub.sendMessage('test.change-listeners')
    assert_equal(testListeners.callCountForChanger,     2)
    assert_equal(testListeners.callCountForNewListener, 1)
    assert_equal(topic.getNumListeners(), 1)

    pub.sendMessage('test.change-listeners')
    assert_equal(testListeners.callCountForChanger,     3)
    assert_equal(testListeners.callCountForNewListener, 1)
