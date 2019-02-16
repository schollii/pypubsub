#!/usr/bin/env python

from pubsub import pub
from pubsub.utils.yamltopicdefnprovider import (
    YamlTopicDefnProvider,
    TOPIC_TREE_FROM_FILE,
    exportTopicTreeSpecYaml
    )
from pubsub.utils.topictreeprinter import printTreeDocs

topicMgr = pub.getDefaultTopicMgr()

def test_yaml_from_file():
    pub.clearTopicDefnProviders()

    provider = YamlTopicDefnProvider('yamlprovider_topics.yaml', TOPIC_TREE_FROM_FILE)
    printTreeDocs()
    print(topicMgr.getTopic('parent', True))
    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None
    assert topicMgr.getOrCreateTopic('parent') is not None
    assert topicMgr.getOrCreateTopic('parent.child') is not None

def test_yaml_import():
    pub.clearTopicDefnProviders()
    topicMgr.delTopic('parent')
    # verify pre:
    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None

    provider = YamlTopicDefnProvider('yamlprovider_topics.yaml', TOPIC_TREE_FROM_FILE)
    pub.addTopicDefnProvider( provider )
    # force instantiation of two topic definitions that were defined in yaml:
    pub.sendMessage('parent', lastname='')
    pub.sendMessage('parent.child', lastname='', nick='')

    # verify post:
    assert topicMgr.getTopic('parent') is not None
    assert topicMgr.getTopic('parent.child') is not None

def test_yaml_string_import():
    str_yaml="""ALL_TOPICS:
  description: Root of all topics
  topics:
  - topic: parent
    description: Parent with a parameter and subtopics
    listenerspec:
    - arg: lastname
      description: surname
    - arg: name
      description: given name
      optional: true
    topics:
    - topic: child
      description: This is the first child
      listenerspec:
      - arg: nick
        description: A nickname
    """

    topicMgr.delTopic('parent')
    pub.clearTopicDefnProviders()
    assert topicMgr.getTopic('parent', True) is None
    assert topicMgr.getTopic('parent.child', True) is None

    provider = YamlTopicDefnProvider(str_yaml)
    pub.addTopicDefnProvider( provider )
    # to force instantiation of two topic definitions that were defined in yaml,
    # this time we just instantiate all of them:
    pub.instantiateAllDefinedTopics(provider)

    printTreeDocs()

    assert topicMgr.getTopic('parent') is not None
    assert topicMgr.getTopic('parent.child') is not None

def test_yaml_topics():
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
