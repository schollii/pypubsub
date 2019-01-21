#!/usr/bin/env python

from pubsub import pub
from pubsub.utils.xmltopicdefnprovider import (
    XmlTopicDefnProvider,
    TOPIC_TREE_FROM_FILE,
    exportTopicTreeSpecXml
    )

topicMgr = pub.getDefaultTopicMgr()

def test_xml_from_file():
    pub.clearTopicDefnProviders()

    provider = XmlTopicDefnProvider('xmlprovider_topics.xml', TOPIC_TREE_FROM_FILE)

    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None
    assert topicMgr.getOrCreateTopic('parent') is not None
    assert topicMgr.getOrCreateTopic('parent.child') is not None

def test_xml_import():
    pub.clearTopicDefnProviders()
    topicMgr.delTopic('parent')
    # verify pre:
    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None

    provider = XmlTopicDefnProvider('xmlprovider_topics.xml', TOPIC_TREE_FROM_FILE)
    pub.addTopicDefnProvider( provider )
    # force instantiation of two topic definitions that were defined in xml:
    pub.sendMessage('parent', lastname='')
    pub.sendMessage('parent.child', lastname='', nick='')

    # verify post:
    assert topicMgr.getTopic('parent') is not None
    assert topicMgr.getTopic('parent.child') is not None

def test_xml_string_import():
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
    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None

    provider = XmlTopicDefnProvider(xml)
    pub.addTopicDefnProvider( provider )
    # to force instantiation of two topic definitions that were defined in xml,
    # this time we just instantiate all of them:
    pub.instantiateAllDefinedTopics(provider)

    assert topicMgr.getTopic('parent') is not None
    assert topicMgr.getTopic('parent.child') is not None

def test_xml_topics():
    # validate that topic specs were properly parsed
    def isValid(topicName, listener):
        topic = topicMgr.getTopic(topicName)
        assert topic.getDescription() is not None
        assert topic.hasMDS()
        return topic.isValid(listener)

    def hello(lastname, name=None): pass
    def friend(lastname, nick, name=None): pass

    assert isValid('parent', hello)
    assert isValid('parent.child', friend)

