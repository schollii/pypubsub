"""
Low level functions and classes related to callables.

The AUTO_TOPIC
is the "marker" to use in callables to indicate that when a message
is sent to those callables, the topic object for that message should be
added to the data sent via the call arguments. See the docs in
CallArgsInfo regarding its autoTopicArgName data member.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.

"""

from inspect import getargspec, ismethod, isfunction
import sys
from types import ModuleType
from typing import Tuple, List, Sequence, Callable, Any

# Opaque constant used to mark a kwarg of a listener as one to which pubsub should assign the topic of the
# message being sent to the listener. This constant should be used by reference; its value is "unique" such that
# pubsub can find such kwarg.
AUTO_TOPIC = '## your listener wants topic object ## (string unlikely to be used by caller)'

# In the user domain, a listener is any callable, regardless of signature. The return value is ignored,
# i.e. the listener will be treated as though it is a Callable[..., None]. Also, the args, "...", must be
# consistent with the MDS of the topic to which listener is being subscribed.
UserListener = Callable[..., Any]


def getModule(obj: Any) -> ModuleType:
    """
    Get the module in which an object was defined.
    :param obj: the object for which to get module
    :return: the module object, or the string '__main__' if no module defined for obj
        (which usually indicates either a builtin, or a definition within main script).
    """
    if hasattr(obj, '__module__'):
        module = obj.__module__
    else:
        module = '__main__'
    return module


def getID(callable_: UserListener) -> Tuple[str, ModuleType]:
    """
    Get "ID" of a callable, in the form of its name and module in which it is defined
    E.g. getID(Foo.bar) returns ('Foo.bar', 'a.b') if Foo.bar was defined in module a.b.
    :param callable\_: a callable, ie function, bound method or callable instance
    """
    sc = callable_
    if ismethod(sc):
        module = getModule(sc.__self__)
        obj_name = '%s.%s' % (sc.__self__.__class__.__name__, sc.__func__.__name__)
    elif isfunction(sc):
        module = getModule(sc)
        obj_name = sc.__name__
    else:  # must be a functor (instance of a class that has __call__ method)
        module = getModule(sc)
        obj_name = sc.__class__.__name__

    return obj_name, module


def getRawFunction(callable_: UserListener) -> Tuple[Callable, int]:
    """
    Get raw function information about a callable.
    :param callable_: any object that can be called
    :return: (func, offset) where func is the function corresponding to callable, and offset is 0 or 1 to
        indicate whether the function's first argument is 'self' (1) or not (0)
    :raise ValueError: if callable_ is not of a recognized type (function, method or object with __call__ method).
    """
    firstArg = 0
    if isfunction(callable_):
        # print 'Function', getID(callable_)
        func = callable_
    elif ismethod(callable_):
        # print 'Method', getID(callable_)
        func = callable_
        if func.__self__ is not None:
            # Method is bound, don't care about the self arg
            firstArg = 1
    elif hasattr(callable_, '__call__'):
        # print 'Functor', getID(callable_)
        func = callable_.__call__
        firstArg = 1  # don't care about the self arg
    else:
        msg = 'type "%s" not supported' % type(callable_).__name__
        raise ValueError(msg)

    return func, firstArg


class ListenerMismatchError(ValueError):
    """
    Raised when an attempt is made to subscribe a listener to
    a topic, but listener does not satisfy the topic's message data
    specification (MDS). This specification is inferred from the first
    listener subscribed to a topic, or from an imported topic tree
    specification (see pub.addTopicDefnProvider()).
    """

    def __init__(self, msg: str, listener: UserListener, *args):
        idStr, module = getID(listener)
        msg = 'Listener "%s" (from module "%s") inadequate: %s' % (idStr, module, msg)
        ValueError.__init__(self, msg)
        self.args = args
        self.msg = msg
        self.module = module
        self.idStr = idStr

    def __str__(self):
        return self.msg


class CallArgsInfo:
    """
    Represent the "signature" of a listener of topic messages: which arguments are
    required vs optional.
    """

    def __init__(self, func: UserListener, firstArgIdx: int, ignoreArgs: Sequence[str] = None):
        """
        :param func: the callable for which to get paramaters info
        :param firstArgIdx: 0 if listener is a function, 1 if listener is a method
        :param ignoreArgs: do not include the given names in the getAllArgs(), getOptionalArgs() and
            getRequiredArgs() return values

        After construction,
        - self.allParams will contain the subset of 'args' without first
          firstArgIdx items,
        - self.numRequired will indicate number of required arguments
          (ie self.allParams[:self.numRequired] are the required args names);
        - self.acceptsAllKwargs = acceptsAllKwargs
        - self.autoTopicArgName will be the name of argument
          in which to put the topic object for which pubsub message is
          sent, or None. This is identified by the argument that has a
          default value of AUTO_TOPIC.

        For instance,
        - listener(self, arg1, arg2=AUTO_TOPIC, arg3=None) will have self.allParams = (arg1, arg2, arg3),
            self.numRequired=1, and self.autoTopicArgName = 'arg2', whereas
        - listener(self, arg1, arg3=None) will have self.allParams = (arg1, arg3), self.numRequired=1, and
            self.autoTopicArgName = None.
        """

        (allParams, varParamName, varOptParamName, defaultVals) = getargspec(func)
        if defaultVals is None:
            defaultVals = []
        else:
            defaultVals = list(defaultVals)

        self.acceptsAllKwargs = (varOptParamName is not None)
        self.acceptsAllUnnamedArgs = (varParamName is not None)

        self.allParams = allParams
        del self.allParams[0:firstArgIdx]  # does nothing if firstArgIdx == 0

        if ignoreArgs:
            for var_name in ignoreArgs:
                required = len(self.allParams) - len(defaultVals)
                index = self.allParams.index(var_name)
                del self.allParams[index]
                if index >= required:
                    del defaultVals[index - required]

            if varOptParamName in ignoreArgs:
                self.acceptsAllKwargs = False
            if varParamName in ignoreArgs:
                self.acceptsAllUnnamedArgs = False

        self.numRequired = len(self.allParams) - len(defaultVals)
        assert self.numRequired >= 0

        # if listener wants topic, remove that arg from args/defaultVals
        self.autoTopicArgName = None
        if defaultVals:
            self.__setupAutoTopic(defaultVals)

    def getAllArgs(self) -> List[str]:
        return tuple(self.allParams)

    def getOptionalArgs(self) -> List[str]:
        return tuple(self.allParams[self.numRequired:])

    def getRequiredArgs(self) -> List[str]:
        """
        Return a tuple of names indicating which call arguments
        are required to be present when pub.sendMessage(...) is called.
        """
        return tuple(self.allParams[:self.numRequired])

    def __setupAutoTopic(self, defaults: List[Any]) -> int:
        """
        Does the listener want topic of message? Returns < 0 if not,
        otherwise return index of topic kwarg within args.
        """
        for indx, defaultVal in enumerate(defaults):
            if defaultVal == AUTO_TOPIC:
                firstKwargIdx = self.numRequired
                self.autoTopicArgName = self.allParams.pop(firstKwargIdx + indx)
                break


def getArgs(callable_: UserListener, ignoreArgs: Sequence[str] = None):
    """
    Get the call paramters of a callable.
    :param callable_: the callable for which to get call parameters
    :param ignoreArgs: optional list of names of parameters of callable_ that should not be in the returned object
    :return: an instance of CallArgsInfo for the given callable_
    :raise ListenerMismatchError: if callable_ is not a callable, or ignoreArgs has an item that is not a call
        param of callable
    """
    # figure out what is the actual function object to inspect:
    try:
        func, firstArgIdx = getRawFunction(callable_)
    except ValueError:
        exc = sys.exc_info()[1]
        raise ListenerMismatchError(str(exc), callable_)

    return CallArgsInfo(func, firstArgIdx, ignoreArgs=ignoreArgs)
