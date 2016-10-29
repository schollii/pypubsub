"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

from typing import Any
from textwrap import dedent
from pathlib import Path
import sys

from pubsub.core import TopicNameError

try:
    from importlib.util import cache_from_source
except ImportError:
    from imp import cache_from_source

import pytest

from pubsub import pub

try:
    Path.write_text  # new in Python 3.5
except AttributeError:
    def write_text(path: Path, text: str):
        with path.open('w') as f:
            f.write(text)
    Path.write_text = write_text


topicMgr = pub.getDefaultTopicMgr()


def try_call(max_times: int, func: callable, *args: Any, func_on_fail: callable = None) -> int:
    """
    Try to call a function.
    :param func: the function to call
    :param args: arguments to give to function
    :param max_times: maximum number of attempts
    :param func_on_fail: when call fails, call this function
    :return: # of calls left (so if 0, ran out of calls, i.e. tried more than max_times)
    """
    retries = 0
    while True:
        try:
            if retries >= max_times:
                break
            func(*args)
            break
        except Exception as exc:
            retries += 1
            if func_on_fail is not None:
                func_on_fail(exc)

    return max_times - retries


def cleanup_py_files(path):
    """Cleanup python file and associated byte-compiled file"""
    path = Path(path)

    if path.exists():
        path.unlink()
    assert not path.exists()

    cached_file = Path(cache_from_source(str(path)))
    if cached_file.exists():
        cached_file.unlink()
    assert not cached_file.exists()


def clear_topic_tree():
    root = topicMgr.getRootAllTopics()
    for topic in list(root.getSubtopics()):
        topicMgr.delTopic(topic.getName())
    topicMgr.clearDefnProviders()


def create_all_defined_topics(*args):
    prov = pub.addTopicDefnProvider(*args)
    return pub.instantiateAllDefinedTopics(prov)


topicDefns2 = '''
    class root_topic_1:
        class subtopic_1:
            class subsubtopic_11:
                """
                Sub sub topic 1 of sub topic 1. Only need to doc the
                extra args.
                """
                def msgDataSpec(arg1, arg3, arg2=None, arg4=None):
                    """
                    - arg3: doc for arg3
                    - arg4: doc for arg4
                    """
                    pass

        '''


class topicDefns3:
    class root_topic_1:
        """Root topic 1"""

        class subtopic_1:
            """
            Sub topic 1 of root topic. Docs rely on one blank line for
            topic doc, and indentation for each argument doc.
            """

            def msgDataSpec(arg1, arg2=None):
                """
                - arg1: some multiline doc
                    for arg1
                - arg2: some multiline doc
                    for arg2
                """
                pass

            class subsubtopic_12:
                """Sub sub topic 2 of sub topic 1."""

                def msgDataSpec(arg1, argA, arg2=None, argB=None):
                    """
                    - argA: doc for argA
                    - argB: doc for argB
                    """
                    pass


failed_imports = []

num_tries = 2000

def teardown_module():
    #print(len(failed_imports) / num_tries)
    pass


# @pytest.mark.parametrize('dummy', range(num_tries))
# def test_import(dummy):
#     from importlib import import_module
#     pytest.raises(ImportError, import_module, 'some_module')
#
#     some_module_path = Path('some_module.py')
#     some_module_path.write_text("")
#     assert some_module_path.exists()
#     assert 'some_module' not in sys.modules
#     assert str(some_module_path.parent.resolve()) in sys.path
#     try:
#         import_module('some_module')
#         del sys.modules['some_module']
#     except ImportError:
#         failed_imports.append(dummy)
#
#     assert try_call(1000, cleanup_py_files, some_module_path)
#

def test_provider():
    clear_topic_tree()

    # create several providers that provide for different subsets of a tree:
    pub.addTopicDefnProvider('my_import_topics')
    pub.addTopicDefnProvider(topicDefns2, pub.TOPIC_TREE_FROM_STRING)
    pub.addTopicDefnProvider(topicDefns3, pub.TOPIC_TREE_FROM_CLASS)

    # adding the providers loaded the specifications, but did not create any topics:
    pytest.raises(TopicNameError, topicMgr.getTopic, 'root_topic_1')
    pytest.raises(TopicNameError, topicMgr.getTopic, 'root_topic_1.subtopic_2')

    # the following will create topics based on the providers added:
    assert topicMgr.getOrCreateTopic('root_topic_1').hasMDS()
    assert topicMgr.getOrCreateTopic('root_topic_1.subtopic_1').hasMDS()
    assert topicMgr.getOrCreateTopic('root_topic_1.subtopic_1.subsubtopic_11').hasMDS()
    assert topicMgr.getOrCreateTopic('root_topic_1.subtopic_1.subsubtopic_12').hasMDS()
    assert topicMgr.getOrCreateTopic('root_topic_1.subtopic_2').hasMDS()
    assert topicMgr.getOrCreateTopic('root_topic_1.subtopic_2.subsubtopic_21').hasMDS()

    # create some listeners and validate them even though none have been subscribed so the MDS
    # will be used in order to validate them:

    def sub(arg1=678):
        pass

    def sub_2(arg1=987, arg2=123):
        pass

    def sub_21(arg1, arg2=None, arg4=None):
        pass

    def isValid(topicName, listener):
        topic = topicMgr.getTopic(topicName)
        assert topic.getDescription()
        assert topic.hasMDS()
        return topic.isValid(listener)

    assert isValid('root_topic_1', sub)
    assert isValid('root_topic_1.subtopic_2', sub_2)
    assert isValid('root_topic_1.subtopic_2.subsubtopic_21', sub_21)

    def sub_21_bad(arg4):  # required arg4 rather than optional!
        pass

    assert not topicMgr.getTopic('root_topic_1.subtopic_2.subsubtopic_21').isValid(sub_21_bad)


@pytest.mark.parametrize('repeat', range(100))
def test_export(repeat):
    # create a topic tree from a couple of the topic providers:
    clear_topic_tree()
    all_topics = create_all_defined_topics(topicDefns2, pub.TOPIC_TREE_FROM_STRING)
    all_topics.extend(create_all_defined_topics(topicDefns3, pub.TOPIC_TREE_FROM_CLASS))

    # export topic tree:
    try_call(100, pub.exportTopicTreeSpec, 'my_exported_topics')

    # import exported tree:
    clear_topic_tree()
    all_topics2 = create_all_defined_topics('my_exported_topics')
    # verify:
    assert sorted(all_topics) == sorted(all_topics2)

    try_call(100, cleanup_py_files, 'my_exported_topics.py')


def test_string_prov_export():
    clear_topic_tree()

    importStr = '''
        """Tree docs, can be anything you want."""

        class root_topic_1:
            """Root topic 1."""

            class subtopic_1:
                """
                Sub topic 1 of root topic. Docs rely on one
                blank line for topic doc, and indentation for
                each argument doc.
                """

                def msgDataSpec(arg1, arg2=None):
                    """
                    - arg1: some multiline doc
                        for arg1
                    - arg2: some multiline doc
                        for arg2
                    """
                    pass

        class root_topic_2:
            """Root topic 2."""

        '''
    pub.clearTopicDefnProviders()
    provider = pub.addTopicDefnProvider(importStr, pub.TOPIC_TREE_FROM_STRING)
    treeDoc = provider.getTreeDoc()
    assert treeDoc == """Tree docs, can be anything you want."""
    root = topicMgr.getOrCreateTopic('root_topic_1.subtopic_1')
    assert root is not None
    assert topicMgr.getOrCreateTopic('root_topic_2').hasMDS()

    # few sanity checks
    def sub_1(arg1, arg2=None): pass

    assert root.hasMDS()
    assert pub.isValid(sub_1, 'root_topic_1.subtopic_1')

    # export tree
    exported = pub.exportTopicTreeSpec(rootTopic='root_topic_1', moduleDoc=treeDoc)
    # print(exported)

    expectExport = '''\
        # Automatically generated by TopicTreeSpecPrinter(**kwargs).
        # The kwargs were:
        # - fileObj: StringIO
        # - footer: '# End of topic tree definition. Note that application may l...'
        # - indentStep: 4
        # - treeDoc: 'Tree docs, can be anything you want....'
        # - width: 70


        """
        Tree docs, can be anything you want.
        """


        class root_topic_1:
            """
            Root topic 1.
            """

            class subtopic_1:
                """
                Sub topic 1 of root topic. Docs rely on one
                blank line for topic doc, and indentation for
                each argument doc.
                """

                def msgDataSpec(arg1, arg2=None):
                    """
                    - arg1: some multiline doc
                        for arg1
                    - arg2: some multiline doc
                        for arg2
                    """


        # End of topic tree definition. Note that application may load
        # more than one definitions provider.
        '''

    # check there are no differences
    from difflib import context_diff, ndiff
    diffs = ndiff(dedent(expectExport).splitlines(), exported.splitlines())
    diffs = [d for d in diffs if not d.startswith(' ')]
    assert diffs == ['- ', '+         ']

    # now for module:
    provider = pub.addTopicDefnProvider('test4_prov_module_expect')
    pub.instantiateAllDefinedTopics(provider)
    modDoc = provider.getTreeDoc()
    assert modDoc.startswith('\nTree docs, can be anything you')
    pub.exportTopicTreeSpec('test4_prov_module_actual',
                            rootTopic='root_topic_1b', moduleDoc=treeDoc)
    lines1 = open('test4_prov_module_actual.py', 'r').readlines()
    lines2 = open('test4_prov_module_expect.py', 'r').readlines()
    diffs = ndiff(lines1, lines2)
    diffs = [d for d in diffs if not d.startswith(' ')]
    assert not list(diffs) or list(diffs) == ['- # - fileObj: TextIOWrapper\n', '+ # - fileObj: file\n']
    Path('test4_prov_module_actual.py').unlink()


def test_module_as_class():
    clear_topic_tree()
    assert topicMgr.getTopic('root_topic_1', True) is None
    assert topicMgr.getTopic('root_topic_2.sub_topic_21', True) is None

    # noinspection PyUnresolvedReferences
    import my_import_topics
    provider = pub.addTopicDefnProvider(my_import_topics, pub.TOPIC_TREE_FROM_CLASS)
    pub.instantiateAllDefinedTopics(provider)

    assert topicMgr.getTopic('root_topic_1') is not None
    assert topicMgr.getTopic('root_topic_2.subtopic_21') is not None

    pub.sendMessage(my_import_topics.root_topic_1)
