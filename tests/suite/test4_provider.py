"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

from typing import Any
from textwrap import dedent
from pathlib import Path
import sys
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
    :return:
    """
    retries = 0
    while True:
        try:
            if retries < max_times:
                func(*args)
            return retries
        except Exception as exc:
            retries += 1
            if func_on_fail is not None:
                func_on_fail(exc)

    return retries


@pytest.mark.parametrize('execution_number', range(1))
def test1(execution_number):
    root = topicMgr.getRootAllTopics()
    for topic in list(root.getSubtopics()):
        topicMgr.delTopic(topic.getName())

    class my_topics:
        class rootTopic1:
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

        class rootTopic2:
            """Root topic 2"""

    pub.addTopicDefnProvider(my_topics, pub.TOPIC_TREE_FROM_CLASS)

    provString = '''
        class rootTopic1:
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

    pub.addTopicDefnProvider(provString, pub.TOPIC_TREE_FROM_STRING)

    provFile = '''
        class rootTopic1:
            class subtopic_2:
                class subsubtopic_21:
                    """Sub sub topic 1 of sub topic 2."""
                    def msgDataSpec(arg1, arg2=None, someArg=456, arg4=None):
                        """
                        - arg1: doc for arg1
                        - arg2: doc for arg2
                        - arg4: doc for arg4
                        """
                        pass
        '''

    # created module file (and confirm it is there):
    myTopicTreePath = Path('myTopicTree.py')
    myTopicTreePath.write_text(dedent(provFile))
    assert myTopicTreePath.exists()
    writePath = myTopicTreePath.parent.resolve()
    assert str(writePath) in sys.path

    # import from it: 
    pub.addTopicDefnProvider('myTopicTree')

    # cleanup file:
    def cleanup_py_files(path):
        path = Path(path)

        if path.exists():
            path.unlink()
        assert not path.exists()

        cached_file = Path(cache_from_source(str(path)))
        if cached_file.exists():
            cached_file.unlink()
        assert not cached_file.exists()

    try_call(100, cleanup_py_files, myTopicTreePath)

    # verify what was imported:
    assert not topicMgr.getTopic('rootTopic1.subtopic_2', okIfNone=True)
    # the following should create all topic tree since parent
    # topics are automatically created
    assert topicMgr.getOrCreateTopic('rootTopic1.subtopic_1.subsubtopic_11')
    assert topicMgr.getOrCreateTopic('rootTopic1.subtopic_1.subsubtopic_12')
    assert topicMgr.getOrCreateTopic('rootTopic1.subtopic_2.subsubtopic_21')

    # validate that topic specs were properly parsed
    def isValid(topicName, listener):
        topic = topicMgr.getTopic(topicName)
        assert topic.getDescription()
        assert topic.hasMDS()
        return topic.isValid(listener)

    def sub():
        pass

    def sub_1(arg1, arg2=123):
        pass

    def sub_11(arg1, arg3, arg2=None, arg4=None):
        pass

    assert isValid('rootTopic1', sub)
    assert isValid('rootTopic1.subtopic_1', sub_1)
    assert isValid('rootTopic1.subtopic_1.subsubtopic_11', sub_11)
    # no providers have spec for subtopic_2
    assert not topicMgr.getTopic('rootTopic1.subtopic_2').hasMDS()

    # printTreeSpec()

    # export topic tree: 
    try_call(100, pub.exportTopicTreeSpec, 'newTopicTree')
    root2Defn = pub.exportTopicTreeSpec(rootTopic='rootTopic1')

    try_call(100, cleanup_py_files, 'newTopicTree.py')


def test2_import_export_no_change():
    #
    # Test that import/export/import does not change the import
    #

    importStr = '''
        """Tree docs, can be anything you want."""

        class test_import_export_no_change:
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
        '''
    pub.clearTopicDefnProviders()
    provider = pub.addTopicDefnProvider(importStr, pub.TOPIC_TREE_FROM_STRING)
    treeDoc = provider.getTreeDoc()
    assert treeDoc == """Tree docs, can be anything you want."""
    root = topicMgr.getOrCreateTopic('test_import_export_no_change.subtopic_1')

    # few sanity checks
    def sub_1(arg1, arg2=None): pass

    assert root.hasMDS()
    assert pub.isValid(sub_1, 'test_import_export_no_change.subtopic_1')

    # export tree
    exported = pub.exportTopicTreeSpec(rootTopic='test_import_export_no_change', moduleDoc=treeDoc)
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


        class test_import_export_no_change:
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
                            rootTopic='test_import_export_no_change2', moduleDoc=treeDoc)
    lines1 = open('test4_prov_module_actual.py', 'r').readlines()
    lines2 = open('test4_prov_module_expect.py', 'r').readlines()
    diffs = ndiff(lines1, lines2)
    diffs = [d for d in diffs if not d.startswith(' ')]
    assert not list(diffs) or list(diffs) == ['- # - fileObj: TextIOWrapper\n', '+ # - fileObj: file\n']
    Path('test4_prov_module_actual.py').unlink()


def test_module_as_class():
    assert topicMgr.getTopic('root_topic1', True) is None
    assert topicMgr.getTopic('root_topic2.sub_topic21', True) is None

    import my_import_topics
    provider = pub.addTopicDefnProvider(my_import_topics, pub.TOPIC_TREE_FROM_CLASS)
    pub.instantiateAllDefinedTopics(provider)

    assert topicMgr.getTopic('root_topic1') is not None
    assert topicMgr.getTopic('root_topic2.sub_topic21') is not None

    pub.sendMessage(my_import_topics.root_topic1)
