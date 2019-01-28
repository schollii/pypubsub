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

from inspect import ismethod, isfunction, signature, Parameter
import sys
from types import ModuleType
from typing import Tuple, List, Sequence, Callable, Any

# Opaque constant used to mark a kwarg of a listener as one to which pubsub should assign the topic of the
# message being sent to the listener. This constant should be used by reference; its value is "unique" such that
# pubsub can find such kwarg.
class AUTO_TOPIC: pass

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


def getID(callable_obj: UserListener) -> Tuple[str, ModuleType]:
    """
    Get "ID" of a callable, in the form of its name and module in which it is defined
    E.g. getID(Foo.bar) returns ('Foo.bar', 'a.b') if Foo.bar was defined in module a.b.
    :param callable_obj: a callable, ie function, bound method or callable instance
    """
    sc = callable_obj
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


def getRawFunction(callable_obj: UserListener) -> Tuple[Callable]:
    """
    Get raw function information about a callable.
    :param callable_obj: any object that can be called
    :return: function corresponding to callable, and offset is 0 or 1 to
        indicate whether the function's first argument is 'self' (1) or not (0)
    :raise ValueError: if callable_obj is not of a recognized type (function, method or object with __call__ method).
    """
    firstArg = 0
    if isfunction(callable_obj):
        # print 'Function', getID(callable_obj)
        func = callable_obj
    elif ismethod(callable_obj):
        # print 'Method', getID(callable_obj)
        func = callable_obj
    elif hasattr(callable_obj, '__call__'):
        # print 'Functor', getID(callable_obj)
        func = callable_obj.__call__
    else:
        msg = 'type "%s" not supported' % type(callable_obj).__name__
        raise ValueError(msg)

    return func


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

    def __init__(self, func: UserListener, ignoreArgs: Sequence[str] = ()):
        """
        :param func: the callable for which to get paramaters info
        :param ignoreArgs: do not include the given names in the get*Args() return values

        After construction,
        - self.acceptsAllKwargs = True if the listener has a **kwargs arg
        - self.autoTopicArgName will be the name of argument in which to put the Topic
          object for which pubsub message is sent, or None if auto off. This is identified
          by a parameter that has a default value of AUTO_TOPIC.

        For instance,
        - listener(self, arg1, arg2=AUTO_TOPIC, arg3=None) will have self.allParams = (arg1, arg2, arg3),
            self.numRequired=1, and self.autoTopicArgName = 'arg2', whereas
        - listener(self, arg1, arg3=None) will have self.allParams = (arg1, arg3), self.numRequired=1, and
            self.autoTopicArgName = None.
        """

        requiredArgs = []
        optionalArgs = []
        self.autoTopicArgName = None
        self.acceptsAllKwargs = False
        for argName, param in signature(func).parameters.items():
            if argName in ignoreArgs or param.kind == Parameter.VAR_POSITIONAL:
                continue

            if param.kind == Parameter.VAR_KEYWORD:
                self.acceptsAllKwargs = True
                continue

            if param.default == Parameter.empty:
                requiredArgs.append(argName)
            else:
                if param.default == AUTO_TOPIC:
                    self.autoTopicArgName = argName
                else:
                    optionalArgs.append(argName)

        self.requiredArgs = tuple(requiredArgs)
        self.optionalArgs = tuple(optionalArgs)
        self.allParams = self.requiredArgs + self.optionalArgs

    def getAllArgs(self) -> Tuple[str]:
        """
        Return a tuple of names indicating the complete set of message data
        (keyword args) that can be given to this listener
        """
        return self.optionalArgs

    def getOptionalArgs(self) -> Tuple[str]:
        """
        Return a tuple of names indicating which message data (keyword args)
        are optional when this listener is called.
        """
        return self.optionalArgs

    def getRequiredArgs(self) -> Tuple[str]:
        """
        Return a tuple of names indicating which message data (keyword args)
        are required when this listener is called.
        """
        return self.requiredArgs


def getArgs(callable_obj: UserListener, ignoreArgs: Sequence[str] = ()) -> CallArgsInfo:
    """
    Get the call parameters of a callable to be used as listener.
    :param callable_obj: the callable for which to get call parameters
    :param ignoreArgs: optional list of names of parameters of callable_obj that should not be in the returned object
    :return: an instance of CallArgsInfo for the given callable_obj
    :raise ListenerMismatchError: if callable_obj is not a callable, or ignoreArgs has an item that is not a call
        param of callable
    """
    # figure out what is the actual function object to inspect:
    try:
        func = getRawFunction(callable_obj)
    except ValueError:
        exc = sys.exc_info()[1]
        raise ListenerMismatchError(str(exc), callable_obj)

    return CallArgsInfo(func, ignoreArgs=ignoreArgs)
