#!/usr/bin/env python

from nose.tools import (
    assert_raises, 
    assert_equal, 
    assert_not_equal,
    assert_true,
)

try: # for Python 2.4:
    from nose.tools import (
        assert_is_not_none, 
        assert_is_none
    )
except ImportError:
    def assert_is_none(what):
        assert_true( what is None )
    def assert_is_not_none(what):
        assert_true( what is not None)

from pubsub import pub
from pubsub.utils.xmltopicdefnprovider import (
    XmlTopicDefnProvider, 
    TOPIC_TREE_FROM_FILE,
    exportTopicTreeSpecXml
    )

topicMgr = pub.getDefaultTopicMgr()

def test0_xml_from_file():
    pub.clearTopicDefnProviders()

    provider = XmlTopicDefnProvider('xmlprovider_topics.xml', TOPIC_TREE_FROM_FILE)
    
    assert_is_none( topicMgr.getTopic('parent', True) )
    assert_is_none( topicMgr.getTopic('parent.child', True) )
    assert_is_not_none( topicMgr.getOrCreateTopic('parent') )
    assert_is_not_none( topicMgr.getOrCreateTopic('parent.child') )

def test1_xml_import():
    pub.clearTopicDefnProviders()
    topicMgr.delTopic('parent')
    # verify pre:
    assert_is_none( topicMgr.getTopic('parent', True) )
    assert_is_none( topicMgr.getTopic('parent.child', True) )

    provider = XmlTopicDefnProvider('xmlprovider_topics.xml', TOPIC_TREE_FROM_FILE)
    pub.addTopicDefnProvider( provider )
    # force instantiation of two topic definitions that were defined in xml:
    pub.sendMessage('parent', lastname='')
    pub.sendMessage('parent.child', lastname='', nick='')
    
    # verify post:
    assert_is_not_none( topicMgr.getTopic('parent') )
    assert_is_not_none( topicMgr.getTopic('parent.child') )

def test2_xml_string_import():
    xml="""<topicdefntree>
      <description>Test Topics showing hierarchy and topic inheritance</description>
      <topic id="parent">
          <description>Parent with a parameter and subtopics</description>
          <listenerspec>
              <arg id="lastname">surname</arg>
              <arg id="name" optional="True">given name</arg>
            </listenerspec>
          <topic id="child">
              <description>This is the first child</description>
              <listenerspec>
                  <arg id="nick">A nickname</arg>
                </listenerspec>
            </topic>
        </topic>
    </topicdefntree>"""

    topicMgr.delTopic('parent')
    pub.clearTopicDefnProviders()
    assert_is_none( topicMgr.getTopic('parent', True) )
    assert_is_none( topicMgr.getTopic('parent.child', True) )

    provider = XmlTopicDefnProvider(xml)
    pub.addTopicDefnProvider( provider )
    # to force instantiation of two topic definitions that were defined in xml, 
    # this time we just instantiate all of them:
    pub.instantiateAllDefinedTopics(provider)

    assert_is_not_none( topicMgr.getTopic('parent') )
    assert_is_not_none( topicMgr.getTopic('parent.child') )

def test3_xml_topics():
    # validate that topic specs were properly parsed
    def isValid(topicName, listener):
        topic = topicMgr.getTopic(topicName)
        assert_is_not_none( topic.getDescription() )
        assert_true( topic.hasMDS() )
        return topic.isValid(listener)

    def hello(lastname, name=None): pass
    def friend(lastname, nick, name=None): pass

    assert_true( isValid('parent', hello) )
    assert_true( isValid('parent.child', friend) )

