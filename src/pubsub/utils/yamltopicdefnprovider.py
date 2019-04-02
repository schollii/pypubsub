"""
Contributed by Tom Harris, adapted by Oliver Schoenborn to be
consistent with pubsub API.

An extension for pubsub (http://pubsub.sourceforge.net) so topic tree
specification can be encoded in YAML format rather than pubsub's default
Python nested class format.

To use:

    yaml = '''
            topicdefntree:
              - description: Test Topics showing hierarchy and topic inheritance
              - topics:
                - id: parent
                  description: Parent with a parameter and subtopics
                  listenerspec:
                    - id: lastname
                      description: surname
                      optional: False
                    - id: lastname
                      description: given name
                      optional: True
                  topics:
                    - id: child
                      description: This is the first child
                      listenerspec:
                        - id: nick
                          description: A nickname
                          optional: False
    '''

These topic definitions are loaded through an YamlTopicDefnProvider:

    pub.addTopicDefnProvider( YamlTopicDefnProvider(yaml) )

The YamlTopicDefnProvider also accepts a filename instead of yaml string:

    provider = YamlTopicDefnProvider("path/to/yamlfile.yaml", TOPIC_TREE_FROM_FILE)
    pub.addTopicDefnProvider( provider )

Topics can be exported to a yaml file using the exportTopicTreeSpecYaml function.
This will create a text file for the yaml and return the string representation
of the yaml tree.

:copyright: Copyright since 2013 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

__author__ = 'Tom Harris'
__revision__ = 0
__date__ = '2019-02-14'

from collections.abc import Iterable
from typing import Any

import voluptuous as vol
import yaml

from ..core.topictreetraverser import ITopicTreeVisitor
from ..core.topicdefnprovider import (
    ITopicDefnProvider,
    ArgSpecGiven,
    TOPIC_TREE_FROM_STRING,
)


__all__ = [
    'YamlTopicDefnProvider',
    'exportTopicTreeSpecYaml',
    'TOPIC_TREE_FROM_FILE'
]


TOPIC_TREE_FROM_FILE = 'file'
TOPIC = 'topic'
TOPICS = 'topics'
TOPIC_DESCRIPTION = 'description'
TOPIC_LISTENER_SPEC = 'listenerspec'
TOPIC_LISTENER_ARG = 'arg'
TOPIC_LISTENR_ARG_OPTIONAL = 'optional'
ALL_TOPICS_NAME = 'ALL_TOPICS'


def string(value: Any) -> str:
    """Coerce value to string, except for None."""
    if value is None:
        raise vol.Invalid('string value is None')
    if isinstance(value, (list, dict)):
        raise vol.Invalid('value should be a string')

    return str(value)


def string_no_space(value: Any) -> str:
    """Coerce value to string with no spaces."""
    return string(value).strip().replace(' ', '_')


def boolean(value: Any) -> bool:
    """Validate and coerce a boolean value."""
    if isinstance(value, str):
        value = value.lower()
        if value in ('1', 'true', 'yes', 'on', 'enable'):
            return True
        if value in ('0', 'false', 'no', 'off', 'disable'):
            return False
        raise vol.Invalid('invalid boolean value {}'.format(value))
    return bool(value)


def print_topic(topic_tree: dict, level=0):
    if topic_tree:
        topic_id = topic_tree.get(TOPIC)
        topic_desc = topic_tree.get(TOPIC_DESCRIPTION)
        print(' ' * level, topic_id, ': ', topic_desc)
        for topic in topic_tree.get(TOPICS, []):
            print_topic(topic, level + 1)


LISTENER_SPEC_SCHEMA = vol.Schema({
    vol.Required(TOPIC_LISTENER_ARG): string_no_space,
    vol.Required(TOPIC_DESCRIPTION): string,
    vol.Optional(TOPIC_LISTENR_ARG_OPTIONAL, True): boolean
})


TOPIC_SCHEMA = vol.Schema({
    vol.Required(TOPIC): string_no_space,
    vol.Required(TOPIC_DESCRIPTION): string,
    vol.Optional(TOPIC_LISTENER_SPEC): [LISTENER_SPEC_SCHEMA],
    vol.Optional(TOPICS, []): [vol.Self]
})

SCHEMA = vol.Schema({
    vol.Required(string_no_space): vol.Schema({
        vol.Required(TOPIC_DESCRIPTION): string,
        vol.Optional(TOPICS, []): [TOPIC_SCHEMA]
    })
})


class YamlTopicDefnProvider(ITopicDefnProvider):
    class YamlParserError(RuntimeError):
        pass

    class UnrecognizedSourceFormatError(ValueError):
        pass

    def __init__(self, yaml_str, format=TOPIC_TREE_FROM_STRING):
        self._topics = {}
        self._treeDoc = ''
        if format == TOPIC_TREE_FROM_FILE:
            with open(yaml_str, 'r') as stream:
                try:
                    yaml_topics = SCHEMA(yaml.load(stream))
                except yaml.YAMLError as err:
                    raise self.YamlParserError(
                        'YAML file format is incorrect, or file missing: %s',
                        err)
                except vol.error.MultipleInvalid as err:
                    raise self.YamlParserError(
                        'YAML file content is incorrect: %s', err)
        elif format == TOPIC_TREE_FROM_STRING:
            try:
                yaml_topics = SCHEMA(yaml.load(yaml_str))
            except vol.error.MultipleInvalid as err:
                raise self.YamlParserError(
                    'YAML string content is incorrect: %s', err)
        else:
            raise self.UnrecognizedSourceFormatError()

        #for topic_tree in yaml_topics:
        for tree_name, _ in yaml_topics.items():
            self._treeDoc = yaml_topics[tree_name][TOPIC_DESCRIPTION]
            self._parse_tree(yaml_topics[tree_name])

    def _parse_tree(self, tree: dict):
        self._treeDoc = tree.get(TOPIC_DESCRIPTION)

        for topic in tree.get(TOPICS, []):
            self._parse_topic(topic)

    def _parse_topic(self, topic, parents=None, specs=None, reqlist=None):
        parents = parents or []
        specs = specs or {}
        reqlist = reqlist or []

        topic_desc = topic.get(TOPIC_DESCRIPTION)

        topic_id = topic.get(TOPIC)

        for spec in topic.get(TOPIC_LISTENER_SPEC, []):
            arg = spec.get(TOPIC_LISTENER_ARG)
            arg_desc = spec.get(TOPIC_DESCRIPTION)
            arg_optional = spec.get(TOPIC_LISTENR_ARG_OPTIONAL)

            if not arg_optional:
                reqlist.append(arg)

            specs[arg] = arg_desc

        defn = ArgSpecGiven(specs, tuple(reqlist))

        parents.append(topic_id)

        self._topics[tuple(parents)] = topic_desc, defn

        for subtopic in topic.get(TOPICS, []):
            self._parse_topic(subtopic, parents[:], specs.copy(), reqlist[:])

    def getDefn(self, topicNameTuple):
        return self._topics.get(topicNameTuple, (None, None))

    def topicNames(self):
        return self._topics.keys()  # dict_keys iter in 3, list in 2

    def getTreeDoc(self):
        return self._treeDoc


class YamlVisitor(ITopicTreeVisitor):
    def __init__(self, rootTopic):
        self._rootTopic = rootTopic
        self.tree = []

    def _startTraversal(self):
        root_dict = {TOPIC_DESCRIPTION: self._rootTopic.getDescription()}
        lsnr_spec = self._get_listenerspec(self._rootTopic)
        if lsnr_spec:
            root_dict[TOPIC_LISTENER_SPEC] = lsnr_spec
        subtopics = []
        for subtopic in self._rootTopic.subtopics:
            topic_dict = self._topic_to_dict(subtopic)
            subtopics.append(topic_dict)
        if subtopic:
            root_dict[TOPICS] = subtopics
        self.tree = {self._rootTopic.getName(): root_dict}

    def _topic_to_dict(self, topicObj):
        if topicObj.isAll():
            topic_id = ALL_TOPICS_NAME
        else:
            topic_id = topicObj.getNodeName()
        topic_desc = topicObj.description
        subtopics = []
        for subtopic in topicObj.subtopics:
            subtopics.append(self._topic_to_dict(subtopic))

        topic_dict = {TOPIC: topic_id,
                      TOPIC_DESCRIPTION: topic_desc}

        listener_spec = self._get_listenerspec(topicObj)
        if listener_spec:
            topic_dict[TOPIC_LISTENER_SPEC] = listener_spec
        if subtopics:
            topic_dict[TOPICS] = subtopics
        return topic_dict

    def _get_listenerspec(self, topicObj):
        req_args, opt_args = topicObj.getArgs()
        listener_spec = []
        if req_args:
            for arg in req_args:
                desc = topicObj.getArgDescriptions()[arg]
                spec = {TOPIC_LISTENER_ARG: arg,
                        TOPIC_DESCRIPTION: desc}
                listener_spec.append(spec)
        if opt_args:
            for arg in opt_args:
                desc = topicObj.getArgDescriptions()[arg]
                spec = {TOPIC_LISTENER_ARG: arg,
                        TOPIC_DESCRIPTION: desc,
                        TOPIC_LISTENR_ARG_OPTIONAL: "True"}
                listener_spec.append(spec)
        return listener_spec


def exportTopicTreeSpecYaml(rootTopic=ALL_TOPICS_NAME, filename=None, bak='bak'):
    """
    Export the topic tree to a YAML file.

    rootTopic: Topic or str - Optional - Top level topic to export, including
    subtopics. If rootTopic is empty ALL_TOPICS is used.

    filename: str - Optional - file name to export to. File extention will be
    '.yaml'

    bak: - str - Optional - file extention to use for backing up existing file.
    """

    if rootTopic is None:
        from .. import pub
        topicMgr = pub.getDefaultTopicMgr()
        rootTopic = topicMgr.getRootAllTopics()
    elif isinstance(rootTopic, str):
        from .. import pub
        topicMgr = pub.getDefaultTopicMgr()
        rootTopic = topicMgr.getTopic(rootTopic)

    visitor = YamlVisitor(rootTopic)
    traverser = pub.TopicTreeTraverser(visitor)
    traverser.traverse(rootTopic)

    tree = SCHEMA(visitor.tree)
    print(tree)
    if filename:
        filename = '%s.yaml' % filename
        with open(filename, 'w') as fulltree:
            yaml.dump(tree, fulltree, default_flow_style=False)
        print(yaml.dump(tree, default_flow_style=False))

    return yaml.dump(tree, default_flow_style=False)
