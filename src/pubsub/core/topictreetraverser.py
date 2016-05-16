"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.

"""

from enum import IntEnum
from .topicobj import Topic


class ITopicTreeVisitor:
    """
    Derive from ITopicTreeVisitor and override one or more of the
    self._*() methods. Give an instance to an instance of
    TopicTreeTraverser.
    """

    def _accept(self, topicObj: Topic):
        """
        Override this to filter nodes of topic tree. Must return
        True (accept node) of False (reject node). Note that rejected
        nodes cause traversal to move to next branch (no children
        traversed).
        """
        return True

    def _startTraversal(self):
        """Override this to define what to do when traversal() starts."""
        pass

    def _onTopic(self, topicObj):
        """Override this to define what to do for each node."""
        pass

    def _startChildren(self):
        """
        Override this to take special action whenever a
        new level of the topic hierarchy is started (e.g., indent
        some output).
        """
        pass

    def _endChildren(self):
        """
        Override this to take special action whenever a
        level of the topic hierarchy is completed (e.g., dedent
        some output).
        """
        pass

    def _doneTraversal(self):
        """Override this to take special action when traversal done."""
        pass


class TreeTraversal(IntEnum):
    """MAP is sequential through topic manager\'s topics map; the other two, through topic tree."""
    DEPTH, BREADTH, MAP = range(3)


class TopicTreeTraverser:
    """
    Supports taking action on every topic in the topic tree. The traverse() method
    traverses a topic tree and calls visitor._onTopic() for each topic in the tree
    that satisfies visitor._accept(). Additionally it calls visitor._startChildren()
    whenever it starts traversing the subtopics of a topic, and
    visitor._endChildren() when it is done with the subtopics. Finally, it calls
    visitor._doneTraversal() when traversal has been completed. The visitor must
    therefore adhere to the ITopicTreeVisitor interface.
    """

    def __init__(self, visitor: ITopicTreeVisitor = None):
        """The visitor, if given, must adhere to API of ITopicTreeVisitor."""
        self.__handler = visitor

    def setVisitor(self, visitor: ITopicTreeVisitor):
        """The visitor must adhere to API of ITopicTreeVisitor."""
        self.__handler = visitor

    def traverse(self, topicObj: Topic, how: TreeTraversal = TreeTraversal.DEPTH, onlyFiltered: bool = True):
        """
        Start traversing tree at topicObj. Note that topicObj is a
        Topic object, not a topic name. The how defines if tree should
        be traversed breadth or depth first. If onlyFiltered is
        False, then all nodes are accepted (_accept(node) not called).

        This method can be called multiple times.
        """
        if how == TreeTraversal.MAP:
            raise NotImplementedError('not yet available')

        self.__handler._startTraversal()

        if how == TreeTraversal.BREADTH:
            self.__traverseBreadth(topicObj, onlyFiltered)
        else:
            assert how == TreeTraversal.DEPTH
            self.__traverseDepth(topicObj, onlyFiltered)

        self.__handler._doneTraversal()

    def __traverseBreadth(self, topicObj: Topic, onlyFiltered: bool):
        visitor = self.__handler

        def extendQueue(subtopics):
            topics.append(visitor._startChildren)
            topics.extend(subtopics)
            topics.append(visitor._endChildren)

        topics = [topicObj]
        while topics:
            topicObj = topics.pop(0)

            if topicObj in (visitor._startChildren, visitor._endChildren):
                topicObj()
                continue

            if onlyFiltered:
                if visitor._accept(topicObj):
                    extendQueue(topicObj.getSubtopics())
                    visitor._onTopic(topicObj)
            else:
                extendQueue(topicObj.getSubtopics())
                visitor._onTopic(topicObj)

    def __traverseDepth(self, topicObj: Topic, onlyFiltered: bool):
        visitor = self.__handler

        def extendStack(topicTreeStack, subtopics):
            topicTreeStack.insert(0, visitor._endChildren)  # marker functor
            # put subtopics in list in alphabetical order
            subtopicsTmp = list(subtopics)
            subtopicsTmp.sort(reverse=True, key=topicObj.__class__.getName)
            for sub in subtopicsTmp:
                topicTreeStack.insert(0, sub)  # this puts them in reverse order
            topicTreeStack.insert(0, visitor._startChildren)  # marker functor

        topics = [topicObj]
        while topics:
            topicObj = topics.pop(0)

            if topicObj in (visitor._startChildren, visitor._endChildren):
                topicObj()
                continue

            if onlyFiltered:
                if visitor._accept(topicObj):
                    extendStack(topics, topicObj.getSubtopics())
                    visitor._onTopic(topicObj)
            else:
                extendStack(topics, topicObj.getSubtopics())
                visitor._onTopic(topicObj)
