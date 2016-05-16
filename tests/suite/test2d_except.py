"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import gc

import pytest

from pubsub import pub

topicMgr = pub.getDefaultTopicMgr()


def throws():
    raise RuntimeError('test')


def testHandleExcept1a():
    from pubsub.utils.exchandling import ExcPublisher
    excPublisher = ExcPublisher( pub.getDefaultTopicMgr() )
    pub.setListenerExcHandler(excPublisher)

    # create a listener that raises an exception:
    from raisinglistener import getRaisingListener
    raisingListener = getRaisingListener()

    pub.setNotificationFlags(all=False)
    pub.subscribe(raisingListener, 'testHandleExcept1a')

    # first test when a listener raises an exception and exception listener also raises!
    class BadUncaughtExcListener:
        def __call__(self, listenerStr=None, excTraceback=None):
            raise RuntimeError('bad exception listener!')
    handler = BadUncaughtExcListener()
    pub.subscribe(handler, ExcPublisher.topicUncaughtExc)
    pytest.raises(pub.ExcHandlerError, pub.sendMessage, 'testHandleExcept1a')
    pub.unsubscribe(handler, ExcPublisher.topicUncaughtExc)


def testHandleExcept1b():
    # create a listener that raises an exception:
    from raisinglistener import getRaisingListener
    raisingListener = getRaisingListener()
    pub.subscribe(raisingListener, 'testHandleExcept1b')

    # subscribe a good exception listener and validate
    # create the listener for uncaught exceptions in listeners:
    class UncaughtExcListener:
        def __call__(self, listenerStr=None, excTraceback=None):
            # verify that information received; first the listenerStr
            assert listenerStr.startswith('raisingListener')
            # next the traceback:
            tb = excTraceback.traceback
            assert len(tb) == 2
            def validateTB(tbItem, eFN, eLine, eFnN):
                assert tbItem[0].endswith(eFN), '%s !~ %s' % (tbItem[0], eFN)
                assert tbItem[1] == eLine
                assert tbItem[2] == eFnN
            validateTB(tb[0], 'raisinglistener.py', 5, 'raisingListener')
            validateTB(tb[1], 'raisinglistener.py', 4, 'nested')
            # next the formatted traceback:
            assert len( excTraceback.getFormattedList() ) == len(tb)+1
            # finally the string for formatted traceback:
            msg = excTraceback.getFormattedString()
            #print 'Msg "%s"' % msg
            assert msg.startswith('  File')
            assert msg.endswith("name 'RuntimeError2' is not defined\n")

    from pubsub.utils.exchandling import ExcPublisher
    topic = topicMgr.getTopic( ExcPublisher.topicUncaughtExc )
    assert not topic.hasListeners()
    handler = UncaughtExcListener()
    pub.subscribe(handler, ExcPublisher.topicUncaughtExc)
    pub.sendMessage('testHandleExcept1b')

    # verify that listener isn't stuck in a cyclic reference by sys.exc_info()
    del raisingListener
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert not topicMgr.getTopic('testHandleExcept1b').hasListeners()
    pub.unsubscribe(handler, ExcPublisher.topicUncaughtExc)


def testHandleExcept2():
    #Test sendMessage when one handler, then change handler and verify changed
    testTopic = 'testTopics.testHandleExcept2'
    pub.subscribe(throws, testTopic)
    pub.setListenerExcHandler(None)
    #pubsub.utils.notification.useNotifyByWriteFile()
    #assert_equal( topicMgr.getTopic(testTopic).getNumListeners(), 1 )

    expect = None

    def validate(className):
        global expect
        assert expect == className
        expect = None

    class MyExcHandler:
        def __call__(self, listener, topicObj):
            validate(self.__class__.__name__)

    class MyExcHandler2:
        def __call__(self, listener, topicObj):
            validate(self.__class__.__name__)

    def doHandling(HandlerClass):
        global expect
        expect = HandlerClass.__name__  #'MyExcHandler'
        excHandler = HandlerClass()
        pub.setListenerExcHandler(excHandler)
        pub.sendMessage(testTopic)
        assert expect is None

    doHandling(MyExcHandler)
    doHandling(MyExcHandler2)

    # restore to no handling and verify:
    pub.setListenerExcHandler(None)
    pytest.raises( RuntimeError, pub.sendMessage, testTopic)


def testNoExceptionHandling1():
    pub.setListenerExcHandler(None)

    def raises():
        raise RuntimeError('test')
    topicMgr.getOrCreateTopic('testNoExceptionTrapping')
    pub.subscribe(raises, 'testNoExceptionTrapping')
    pytest.raises( RuntimeError, pub.sendMessage, 'testNoExceptionTrapping')


def testNoExceptionHandling2():
    testTopic = 'testTopics.testNoExceptionHandling'
    pub.subscribe(throws, testTopic)
    assert pub.getListenerExcHandler() is None
    pytest.raises( RuntimeError, pub.sendMessage, testTopic)


