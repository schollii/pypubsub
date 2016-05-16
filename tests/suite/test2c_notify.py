"""
This one tests NotifyByWriteFile and custom notification handler

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import io
import gc
from difflib import unified_diff

# setup notification and logging
from pubsub import pub
from pubsub.utils.notification import useNotifyByWriteFile
from pubsub.core import INotificationHandler

topicMgr = pub.getDefaultTopicMgr()

def captureStdout():
    capture = io.StringIO()
    useNotifyByWriteFile( fileObj = capture )
    return capture


def testNotifyByPrint():
    capture = captureStdout()

    def listener1(arg1):
        pass
    pub.subscribe(listener1, 'baz')
    pub.sendMessage('baz', arg1=123)
    pub.unsubscribe(listener1, 'baz')

    def doa():
        def listener2():
            pass
        pub.subscribe(listener2, 'bar')
    doa() # listener2 should be gc'd
    gc.collect() # for pypy: the gc doesn't work the same as cpython's

    topicMgr.delTopic('baz')

    expect = """\
PUBSUB: New topic "baz" created
PUBSUB: Subscribed listener "listener1" to topic "baz"
PUBSUB: Start sending message of topic "baz"
PUBSUB: Sending message of topic "baz" to listener listener1
PUBSUB: Done sending message of topic "baz"
PUBSUB: Unsubscribed listener "listener1" from topic "baz"
PUBSUB: New topic "bar" created
PUBSUB: Subscribed listener "listener2" to topic "bar"
PUBSUB: Listener "listener2" of Topic "bar" has died
PUBSUB: Topic "baz" destroyed
"""
    captured = capture.getvalue()
    #print captured
    #print repr(expect)
    assert captured == expect, \
        '\n'.join( unified_diff(expect.splitlines(), captured.splitlines(), n=0) )


def testFlagChanges():
    savedFlags = pub.getNotificationFlags()

    pub.setNotificationFlags(all=True, sendMessage=False, deadListener=False)
    flags = pub.getNotificationFlags()
    assert not flags['sendMessage']
    assert not flags['deadListener']
    assert flags['newTopic']
    assert flags['delTopic']
    assert flags['subscribe']
    assert flags['unsubscribe']

    pub.setNotificationFlags(subscribe=False, deadListener=True)
    flags = pub.getNotificationFlags()
    assert not flags['sendMessage']
    assert not flags['subscribe']
    assert flags['newTopic']
    assert flags['delTopic']
    assert flags['deadListener']
    assert flags['unsubscribe']

    pub.setNotificationFlags(all=False, subscribe=True, unsubscribe=True)
    flags = pub.getNotificationFlags()
    assert not flags['sendMessage']
    assert not flags['deadListener']
    assert not flags['newTopic']
    assert not flags['delTopic']
    assert flags['subscribe']
    assert flags['unsubscribe']

    pub.setNotificationFlags(** savedFlags)


def testNotifications():
    class Handler(INotificationHandler):
        def __init__(self):
            self.resetCounts()
        def resetCounts(self):
            self.counts = dict(send=0, sub=0, unsub=0, delt=0, newt=0, dead=0, all=0)
        def notifySubscribe(self, pubListener, topicObj, newSub):
            self.counts['sub'] += 1
        def notifyUnsubscribe(self, pubListener, topicObj):
            self.counts['unsub'] += 1
        def notifyDeadListener(self, pubListener, topicObj):
            self.counts['dead'] += 1
        def notifySend(self, stage, topicObj, pubListener=None):
            if stage == 'pre': self.counts['send'] += 1
        def notifyNewTopic(self, topicObj, description, required, argsDocs):
            self.counts['newt'] += 1
        def notifyDelTopic(self, topicName):
            self.counts['delt'] += 1

    notifiee = Handler()
    pub.addNotificationHandler(notifiee)
    pub.setNotificationFlags(all=True)

    def verify(**ref):
        gc.collect() # for pypy: the gc doesn't work the same as cpython's
        for key, val in notifiee.counts.items():
            if key in ref:
                assert val == ref[key], "\n%s\n%s" % (notifiee.counts, ref)
            else:
                assert val == 0, "%s = %s, expected 0" % (key, val)
        notifiee.resetCounts()

    verify()
    def testListener(): pass
    def testListener2(): pass
    def testListener3(): pass
    class TestListener:
        def __call__(self): pass
        def __del__(self): pass
    testListener = TestListener()

    topicMgr = pub.getDefaultTopicMgr()
    topicMgr.getOrCreateTopic('newTopic')
    verify(newt=1)

    pub.subscribe(testListener, 'newTopic')
    pub.subscribe(testListener2, 'newTopic')
    pub.subscribe(testListener3, 'newTopic')
    verify(sub=3)

    pub.sendMessage('newTopic')
    verify(send=1)

    verify(dead=0)
    del testListener
    del testListener3
    verify(dead=2)

    pub.unsubscribe(testListener2,'newTopic')
    verify(unsub=1)

    topicMgr.delTopic('newTopic')
    verify(delt=1)
