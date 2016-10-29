"""
This test suite exercises parts of pubsub that are specific to arg1
messaging protocol. Code that is common to all protocol is tested
elsewhere. Therefore, the tests aim to specifically exercise the
code in the pubsub/core/arg1 folder such that coverage of files
in that folder is almost 100%, and no regard is given to coverage
of other files.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

topics = '''
class topic1:
    """docs for topic1"""

    class subtopic11:
        """docs for subtopic11"""

class topic2:
    """docs for topic2"""
'''

from nose.tools import assert_raises

from pubsub import setuparg1
from pubsub import pub


def test1():
    pub.addTopicDefnProvider(topics, format=pub.TOPIC_TREE_FROM_STRING)
    pub.sendMessage('topic1', 123)
    def listener1a(msg):
        data = msg.data
        msgStr = str(msg)
    def listener1b(*msgs):
        pass
    def listener1c(msg=None, *args):
        pass
    def listener11(msg, topic=pub.AUTO_TOPIC):
        data = msg.data
    pub.subscribe(listener1a, 'topic1')
    pub.subscribe(listener1b, 'topic1')
    pub.subscribe(listener1c, 'topic1')
    pub.subscribe(listener11, 'topic1.subtopic11')
    pub.sendMessage('topic1.subtopic11', 123)

    def badListener1(): pass
    def badListener2(arg1, arg2): pass
    assert_raises(pub.ListenerMismatchError, pub.subscribe, badListener1, 'topic1')
    assert_raises(pub.ListenerMismatchError, pub.subscribe, badListener2, 'topic1')
    #assert_raises(pub.ListenerMismatchError, pub.subscribe, badListener3, 'topic1')

    setuparg1.enforceArgName('someArgName')
    assert_raises(pub.ListenerMismatchError, pub.subscribe, listener1a, 'topic2')

    pub.exportTopicTreeSpec()
    