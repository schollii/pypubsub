"""
:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

from typing import Tuple, List, Sequence, Mapping, Dict, Callable, Any, Optional, Union, TextIO

from .annotations import annotationType


@annotationType
class Topic:
    pass


class TopicNameError(ValueError):
    """
    Raised when the topic name is not properly formatted or
    no corresponding Topic object found.
    """

    def __init__(self, name: str, msg: str):
        ValueError.__init__(self, 'Topic name "%s": %s' % (name, msg))


class TopicDefnError(RuntimeError):
    """
    Raised when an operation requires a topic have an MDS, but it doesn't.
    See also pub.setTopicUnspecifiedFatal().
    """

    def __init__(self, topicNameTuple: Sequence[str]):
        msg = "No topic specification for topic '%s'." % '.'.join(topicNameTuple)
        RuntimeError.__init__(self, msg +
                              " See pub.addTopicDefnProvider() and/or pub.setTopicUnspecifiedFatal()")


class MessageDataSpecError(RuntimeError):
    """
    Raised when an attempt is made to define a topic's Message Data
    Specification (MDS) to something that is not valid.

    The keyword names for invalid data go in the 'args' list,
    and the msg should state the problem and contain "%s" for the
    args, such as MessageDataSpecError('duplicate args %s', ('arg1', 'arg2')).
    """

    def __init__(self, msg: str, args: Sequence[str]):
        argsMsg = msg % ','.join(args)
        RuntimeError.__init__(self, 'Invalid message data spec: ' + argsMsg)


class ExcHandlerError(RuntimeError):
    """
    Raised when a listener exception handler (see pub.setListenerExcHandler())
    raises an exception. The original exception is contained.
    """

    def __init__(self, badExcListenerID: str, topicObj: Topic, origExc: Exception = None):
        """
        The badExcListenerID is the name of the listener that raised
        the original exception that handler was attempting to handle.
        The topicObj is the Topic object for the topic of the
        sendMessage that had an exception raised.
        The origExc is the exception that was raised.
        """
        self.badExcListenerID = badExcListenerID
        import traceback
        self.exc = traceback.format_exc()
        msg = 'The exception handler registered with pubsub raised an ' \
              + 'exception, *while* handling an exception raised by listener ' \
              + ' "%s" of topic "%s"):\n%s' \
                % (self.badExcListenerID, topicObj.getName(), self.exc)
        RuntimeError.__init__(self, msg)


class UnrecognizedSourceFormatError(ValueError):
    """
    Raised when a topic definition provider doesn't recognize the format
    of source input it was given.
    """

    def __init__(self):
        ValueError.__init__(self, 'Source format not recognized')
