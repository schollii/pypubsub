"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

from pubsub import pub
from pubsub.utils.notification import useNotifyByPubsubMessage
topicMgr = pub.getDefaultTopicMgr()


def test_NotificationTopics():
    assert not topicMgr.getTopic('pubsub', okIfNone=True)
    useNotifyByPubsubMessage()
    assert topicMgr.getTopic('pubsub')

    assert topicMgr.getTopic('pubsub').hasSubtopic()

    pubsubTopicNames = [obj.getName() for obj in topicMgr.getTopic('pubsub').getSubtopics()]
    assert (
        set( pubsubTopicNames ) ==
        set(['pubsub.sendMessage', 'pubsub.deadListener',
             'pubsub.subscribe',   'pubsub.unsubscribe',
             'pubsub.newTopic',    'pubsub.delTopic']))


def test_SubscribeNotify():
    class MyListener:
        countSub = 0
        countUnsub = 0
        def listenerSub(self, msgTopic=pub.AUTO_TOPIC, listener=None, topic=None, newSub=None):
            assert msgTopic.getName() == 'pubsub.subscribe'
            assert topic.getName() in ('pubsub.unsubscribe', 'testSubscribeNotify')
            if newSub:
                self.countSub += 1
        def listenerUnsub(self, msgTopic=pub.AUTO_TOPIC, topic=None, listener=None, listenerRaw=None):
            assert topic.getName() in ('testSubscribeNotify', 'pubsub.subscribe' )
            assert msgTopic.getName() == 'pubsub.unsubscribe'
            if listener is not None:
                self.countUnsub += 1
        def listenerTest(self):
            raise NotImplementedError # should never get here

    pub.setNotificationFlags(subscribe=True, unsubscribe=True)
    topicMgr.getOrCreateTopic('testSubscribeNotify')
    tmp = MyListener()

    pub.subscribe(tmp.listenerSub, 'pubsub.subscribe')
    assert tmp.countSub == 0   # don't notify of self subscription
    assert tmp.countUnsub == 0
    sl, ok = pub.subscribe(tmp.listenerUnsub, 'pubsub.unsubscribe')
    assert ok
    assert tmp.countSub == 1
    assert tmp.countUnsub == 0

    pub.subscribe(tmp.listenerTest, 'testSubscribeNotify')
    #assert_equal(tmp.countSub, 2)
    assert tmp.countUnsub == 0
    pub.unsubscribe(tmp.listenerTest, 'testSubscribeNotify')
    #assert_equal(tmp.countSub, 2)
    assert tmp.countUnsub == 1

    pub.unsubscribe(tmp.listenerSub,   'pubsub.subscribe')
    assert tmp.countSub == 2
    assert tmp.countUnsub == 2
    pub.unsubscribe(tmp.listenerUnsub, 'pubsub.unsubscribe')
    assert tmp.countSub == 2
    assert tmp.countUnsub == 2 # don't notify of self unsubscription


def test_SendNotify():
    # trap the pubsub.sendMessage topic:
    class SendHandler:
        def __init__(self):
            self.pre = self.post = 0
        def __call__(self, topic=None, stage=None, listener=None, msgTopic=pub.AUTO_TOPIC):
            if stage == 'pre':
                self.pre += 1
            else:
                self.post += 1
            assert msgTopic.getName() == 'pubsub.sendMessage'
            assert topic.getName() == 'testSendNotify'
    sh = SendHandler()
    pub.subscribe(sh, 'pubsub.sendMessage')
    pub.setNotificationFlags(sendMessage=True)

    # generate a message that will cause pubsub.sendMessage to be generated too
    assert sh.pre == 0
    assert sh.post == 0
    topicMgr.getOrCreateTopic('testSendNotify')
    pub.sendMessage('testSendNotify')
    assert sh.pre == 1
    assert sh.post == 1


