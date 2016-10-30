"""
Top-level functionality related to message listeners.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

from types import ModuleType
from typing import Callable, Mapping, Any, Sequence

from .callables import (
    getID,
    getArgs,
    ListenerMismatchError,
    CallArgsInfo,
    AUTO_TOPIC as _AUTO_ARG,
    UserListener,
)
from .weakmethod import getWeakRef, WeakRef
from .annotations import annotationType

__all__ = [
    'Listener',
    'IListenerExcHandler',
    'ListenerValidator'
]


@annotationType
class Topic:
    pass


@annotationType
class Listener:
    """Wrapper of a UserListener"""
    pass


class IListenerExcHandler:
    """
    Interface class base class for any handler given to pub.setListenerExcHandler()
    Such handler is called whenever a listener raises an exception during a
    pub.sendMessage(). Example::

        from pubsub import pub

        class MyHandler(pub.IListenerExcHandler):
            def __call__(self, listenerID, topicObj):
                ... do something with listenerID ...

        pub.setListenerExcHandler(MyHandler())

    Without an exception handler, the sendMessage() will fail.
    """

    def __call__(self, listenerID: str, topicObj: Topic):
        raise NotImplementedError('%s must override __call__()' % self.__class__)


class Listener:
    """
    Wraps a callable (UserListener) so it can be stored by weak reference and introspected
    to verify that it adheres to a topic's MDS.

    A Listener instance has the same hash value as the callable that it wraps.

    Callables that have 'argName=pub.AUTO_TOPIC' as a kwarg will
    be given the Topic object for the message sent by sendMessage().
    Such a Listener will have wantsTopicObjOnCall() True.

    Callables that have a '\**kargs' argument will receive all message data, not just that for
    the topic they are subscribed to. Such a listener will have wantsAllMessageData() True.
    """

    AUTO_TOPIC = _AUTO_ARG

    def __init__(self, callable_: UserListener, argsInfo: CallArgsInfo, curriedArgs: Mapping[str, Any] = None,
                 onDead: Callable[[Listener], None] = None):
        """
        Use callable_ as a listener of topicName. The argsInfo is the
        return value from a Validator, ie an instance of callables.CallArgsInfo.
        If given, the onDead will be called with self as parameter, if/when
        callable_ gets garbage collected (callable_ is held only by weak
        reference).
        """
        # set call policies
        self.acceptsAllKwargs = argsInfo.acceptsAllKwargs
        self.curriedArgs = curriedArgs

        self._autoTopicArgName = argsInfo.autoTopicArgName
        self._callable = getWeakRef(callable_, self.__notifyOnDead)
        self.__onDead = onDead

        # save identity now in case callable dies:
        name, mod = getID(callable_)  #
        self.__nameID = name
        self.__module = mod
        self.__id = str(id(callable_))[-4:]  # only last four digits of id
        self.__hash = hash(callable_)

    def name(self) -> str:
        """
        Return a human readable name for listener, based on the
        listener's type name and its id (as obtained from id(listener)). If
        caller just needs name based on type info, specify instance=False.
        Note that the listener's id() was saved at construction time (since
        it may get garbage collected at any time) so the return value of
        name() is not necessarily unique if the callable has died (because
        id's can be re-used after garbage collection).
        """
        return '%s_%s' % (self.__nameID, self.__id)

    def typeName(self) -> str:
        """
        Get a type name for the listener. This is a class name or
        function name, as appropriate.
        """
        return self.__nameID

    def module(self) -> ModuleType:
        """
        Get the module in which the callable was defined.
        """
        return self.__module

    def getCallable(self) -> UserListener:
        """
        Get the listener that was given at initialization. Note that
        this could be None if it has been garbage collected (e.g. if it was
        created as a wrapper of some other callable, and not stored
        locally).
        """
        return self._callable()

    def isDead(self) -> bool:
        """Return True if this listener died (has been garbage collected)"""
        return self._callable() is None

    def wantsTopicObjOnCall(self) -> bool:
        """True if this listener wants topic object: it has a arg=pub.AUTO_TOPIC"""
        return self._autoTopicArgName is not None

    def wantsAllMessageData(self) -> bool:
        """True if this listener wants all message data: it has a \**kwargs argument"""
        return self.acceptsAllKwargs

    def setCurriedArgs(self, **curriedArgs):
        """
        Curry the wrapped listener so it appears to *not* have list(curriedArgs) among its parameters.
        The curriedArgs key-value pairs will be given to wrapped listener at call time.
        """
        if curriedArgs.keys() != self.curriedArgs.keys():
            raise ValueError(
                "Listener '{}' already subscribed with a different set of pure curried args ({} != {})"
                .format(self, curriedArgs.keys(), self.curriedArgs.keys()))

        self.curriedArgs = curriedArgs

    def _unlinkFromTopic_(self):
        """Tell self that it is no longer used by a Topic. This allows to break some cyclical references."""
        self.__onDead = None

    def _calledWhenDead(self):
        raise RuntimeError('BUG: Dead Listener called, still subscribed!')

    def __notifyOnDead(self, _: WeakRef):
        """This gets called when listener weak ref has died. Propagate info to Topic."""
        notifyDeath = self.__onDead
        self._unlinkFromTopic_()
        if notifyDeath is not None:
            notifyDeath(self)

    def __eq__(self, rhs: Listener):
        """
        Compare for equality to rhs. This returns true if rhs has our id id(rhs) is same as
        id(self) or id(callable in self).
        """
        if id(self) == id(rhs):
            return True

        c1 = self._callable()
        try:
            c2 = rhs._callable()
        except Exception:
            # then rhs is not a Listener, compare with c1
            return c1 == rhs

        # both side of == are Listener, but always compare unequal if both dead
        if c2 is None and c1 is None:
            return False

        return c1 == c2

    def __ne__(self, rhs: Listener):
        """Counterpart to __eq__ MUST be defined... equivalent to 'not (self == rhs)'."""
        return not self.__eq__(rhs)

    def __hash__(self):
        """
        Hash is an optimization for dict/set searches, it need not return different numbers for every different object.
        """
        return self.__hash

    def __str__(self):
        """String rep is the callable"""
        return self.__nameID

    def __call__(self, kwargs: Mapping[str, Any], actualTopic: Topic, allKwargs: Mapping[str, Any] = None):
        """
        Call the listener with **kwargs. Note that it raises RuntimeError
        if listener is dead. Should always return True (False would require
        the callable_ be dead but self hasn't yet been notified of it...).
        """
        if self.acceptsAllKwargs:
            kwargs = allKwargs or kwargs  # if allKwargs is None then use kwargs

        orig_kwargs = kwargs

        # combine with curried args; Note: this overrides topic arg if present:
        if self.curriedArgs:
            if kwargs:
                kwargs = kwargs.copy()
                kwargs.update(self.curriedArgs)
            else:
                kwargs = self.curriedArgs

        if self._autoTopicArgName is not None:
            if kwargs is orig_kwargs:
                kwargs = kwargs.copy()
            kwargs[self._autoTopicArgName] = actualTopic

        # call:
        cb = self._callable()
        if cb is None:
            self._calledWhenDead()
        cb(**kwargs)

        return True


class ListenerValidator:
    """
    Validates listeners. It checks whether the listener given to
    validate() method complies with required and optional arguments
    specified for topic.

    Do not accept any required args or *args; accept any **kwarg,
    and require that the Listener have at least all the kwargs (can
    have extra) of Topic.
    """

    def __init__(self, topicArgs: Sequence[str], topicKwargs: Sequence[str]):
        """
        :param topicArgs: list of argument names that will be required when sending
            a message to listener. Hence order of items in topicArgs matters.
        :param topicKwargs: list of argument names that will be optional, ie given as keyword arguments
            when sending a message to listener. The list is unordered. """
        self._topicArgs = set(topicArgs)
        self._topicKwargs = set(topicKwargs)

    def validate(self, listener: UserListener, curriedArgNames: Sequence[str] = None) -> CallArgsInfo:
        """
        Validate that listener (with, optionally, given curried parameters) satisfies the requirements of
        being a topic listener.

        :param listener: the callable to validate
        :param curriedArgNames: the list of parameter names to treat as curried
        :returns: a CallArgsInfo object containing information about the listener's call arguments, such as
            whether listener wants topic name (signified by a kwarg value = AUTO_TOPIC in listener signature).
        :raises ListenerMismatchError: if listener not usable for topic
        """
        paramsInfo = getArgs(listener)
        self.__validateArgs(listener, paramsInfo, curriedArgNames)

        return paramsInfo

    # noinspection PyIncorrectDocstring
    def isValid(self, listener: UserListener, curriedArgNames: Sequence[str] = None) -> bool:
        """Same as validate() but returns True/False instead of raising an exception."""
        try:
            self.validate(listener, curriedArgNames=curriedArgNames)
            return True
        except ListenerMismatchError:
            return False

    def __validateArgs(self, listener: UserListener, paramsInfo: CallArgsInfo, curriedArgNames: Sequence[str]):
        # accept **kwargs
        # accept *args

        # check if listener missing params (only possible if
        # paramsInfo.acceptsAllKwargs is False)
        if not paramsInfo.acceptsAllKwargs:
            allTopicMsgArgs = self._topicArgs | self._topicKwargs
            allParams = set(paramsInfo.allParams)
            missingParams = allTopicMsgArgs - allParams
            if missingParams:
                msg = 'needs to accept %s more args (%s)' \
                      % (len(missingParams), ', '.join(missingParams))
                raise ListenerMismatchError(msg, listener, missingParams)
        else:
            # then can accept that some parameters missing from listener
            # signature
            pass

        if curriedArgNames:
            unrecognizedCurried = set(curriedArgNames).difference(paramsInfo.allParams)
            if unrecognizedCurried:
                msg = 'does not have following args: (%s)' % ', '.join(unrecognizedCurried)
                raise ListenerMismatchError(msg, listener, unrecognizedCurried)

            curriedTopicArgs = set(curriedArgNames).intersection(self._topicArgs | self._topicKwargs)
            if curriedTopicArgs:
                msg = 'curried args (%s) are topic args, not allowed' % ', '.join(curriedTopicArgs)
                raise ListenerMismatchError(msg, listener, curriedTopicArgs)

        # check if there are extra required parameters in listener signature:
        extraArgs = set(paramsInfo.getRequiredArgs()) - self._topicArgs
        if extraArgs and curriedArgNames:
            extraArgs = extraArgs.difference(curriedArgNames)
        if extraArgs:
            msg = 'required args (%s) not allowed (could curry them), ' % ','.join(extraArgs)
            if self._topicArgs:
                msg += 'topic req\'d args are (%s)' % ', '.join(self._topicArgs)
            else:
                msg += 'topic has no required args'

            # now make sure listener doesn't require params that are optional in TMS:
            missingDefaultVals = extraArgs.intersection(self._topicKwargs)
            if missingDefaultVals:
                msg += ' (params (%s) are req\'d in listener, optional in topic )' % ', '.join(missingDefaultVals)

            raise ListenerMismatchError(msg, listener, extraArgs)
