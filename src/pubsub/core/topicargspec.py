"""
Definitions related to message data specification.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

import weakref
from typing import Tuple, List, Sequence as Seq, Mapping, Dict, Callable, Any, Optional, Union

from .topicutils import stringize, WeakNone
from .annotations import annotationType
from .topicexc import MessageDataSpecError
from .listener import getArgs as getListenerArgs, UserListener


ArgsDocs = Dict[str, str]
MsgData = Mapping[str, Any]


def verifyArgsDifferent(allArgs, allParentArgs, topicName):
    """
    Verify that allArgs does not contain any of allParentArgs. Raise
    MessageDataSpecError if fail.
    """
    extra = set(allArgs).intersection(allParentArgs)
    if extra:
        msg = 'Args %%s already used in parent of "%s"' % topicName
        raise MessageDataSpecError(msg, tuple(extra))


def verifySubset(all, sub, topicName, extraMsg=''):
    """
    Verify that sub is a subset of all for topicName. Raise
    MessageDataSpecError if fail.
    """
    notInAll = set(sub).difference(all)
    if notInAll:
        args = ','.join(all)
        msg = 'Params [%s] missing inherited [%%s] for topic "%s"%s' % (args, topicName, extraMsg)
        raise MessageDataSpecError(msg, tuple(notInAll))


def topicArgsFromCallable(_callable: UserListener, ignoreArgs: Seq[str] = ()) -> Tuple[ArgsDocs, List[str]]:
    """
    Get the topic message data names and list of those that are required,
    by introspecting given callable. Returns a pair, (args, required)
    where args is a dictionary of allowed message data names vs docstring,
    and required states which ones are required rather than optional.
    """
    argsInfo = getListenerArgs(_callable, ignoreArgs=ignoreArgs)
    required = argsInfo.getRequiredArgs()
    defaultDoc = 'UNDOCUMENTED'
    args = dict.fromkeys(argsInfo.allParams, defaultDoc)
    return args, required


class ArgSpecGiven:
    """
    The message data specification (MDS) for a topic.

    This consists of each argument name that listener should have in its
    signature, plus which ones are required in any sendMessage(), and a
    documentation string for each argument. This instance will be transformed
    into an ArgsInfo object which is basically a superset of that information,
    needed to ensure that the arguments specifications satisfy
    pubsub policies for chosen API version.
    """

    SPEC_GIVEN_NONE = 1  # specification not given
    SPEC_GIVEN_ALL = 3  # all args specified

    def __init__(self, argsDocs: ArgsDocs = None, reqdArgs: Seq[str] = None):
        self.reqdArgs = tuple(reqdArgs or ())

        if argsDocs is None:
            self.argsSpecType = ArgSpecGiven.SPEC_GIVEN_NONE
            self.argsDocs = {}
        else:
            self.argsSpecType = ArgSpecGiven.SPEC_GIVEN_ALL
            self.argsDocs = argsDocs

            # check that all args marked as required are in argsDocs
            missingArgs = set(self.reqdArgs).difference(self.argsDocs.keys())  # py3: iter keys ok
            if missingArgs:
                msg = 'Params [%s] missing inherited required args [%%s]' % ','.join(argsDocs.keys())  # iter keys ok
                raise MessageDataSpecError(msg, missingArgs)

    def setAll(self, allArgsDocs: ArgsDocs, reqdArgs: Seq[str] = None):
        self.argsDocs = allArgsDocs
        self.reqdArgs = reqdArgs or ()
        self.argsSpecType = ArgSpecGiven.SPEC_GIVEN_ALL

    def isComplete(self) -> bool:
        """Returns True if the definition is usable, false otherwise."""
        return self.argsSpecType == ArgSpecGiven.SPEC_GIVEN_ALL

    def getOptional(self) -> List[str]:
        """Get the list of optional arguments"""
        return tuple(set(self.argsDocs.keys()).difference(self.reqdArgs))

    def __str__(self):
        return "%s, %s, %s" % (self.argsDocs, self.reqdArgs, self.argsSpecType)


class SenderMissingReqdMsgDataError(RuntimeError):
    """
    Raised when a sendMessage() is missing arguments tagged as
    'required' by pubsub topic of message.
    """

    def __init__(self, topicName: str, argNames: Seq[str], missing: Seq[str]):
        argsStr = ','.join(argNames)
        missStr = ','.join(missing)
        msg = "Some required args missing in call to sendMessage('%s', %s): %s" \
              % (stringize(topicName), argsStr, missStr)
        RuntimeError.__init__(self, msg)


class SenderUnknownMsgDataError(RuntimeError):
    """
    Raised when a sendMessage() has arguments not listed among the topic's
    message data specification (MDS).
    """

    def __init__(self, topicName: str, argNames: Seq[str], extra: Seq[str]):
        argsStr = ','.join(argNames)
        extraStr = ','.join(extra)
        msg = "Some optional args unknown in call to sendMessage('%s', %s): %s" \
              % (topicName, argsStr, extraStr)
        RuntimeError.__init__(self, msg)


@annotationType
class ArgsInfo:
    pass


class ArgsInfo:
    """
    Encode the Message Data Specification (MDS) for a given
    topic. ArgsInfos form a tree identical to that of Topics in that
    ArgInfos have a reference to their parent and children ArgInfos,
    created for the parent and children topics.

    The only difference
    between an ArgsInfo and an ArgSpecGiven is that the latter is
    what "user thinks is ok" whereas former has been validated:
    the specification for this topic is a strict superset of the
    specification of its parent, and a strict subset of the
    specification of each of its children. Also, the instance
    can be used to check validity and filter arguments.

    The MDS can be created "empty", ie "incomplete", meaning it cannot
    yet be used to validate listener subscriptions to topics.
    """

    SPEC_MISSING = 10  # no args given
    SPEC_COMPLETE = 12  # all args, but not confirmed via user spec

    def __init__(self, topicNameTuple: Seq[str], specGiven: ArgSpecGiven, parentArgsInfo: ArgsInfo):
        self.topicNameTuple = topicNameTuple
        self.allOptional = ()  # topic message optional arg names
        self.allDocs = {}  # doc for each arg
        self.allRequired = ()  # topic message required arg names
        self.argsSpecType = self.SPEC_MISSING
        self.parentAI = WeakNone()
        if parentArgsInfo is not None:
            self.parentAI = weakref.ref(parentArgsInfo)
            parentArgsInfo.__addChildAI(self)
        self.childrenAI = []

        if specGiven.isComplete():
            self.__setAllArgs(specGiven)

        if parentArgsInfo is None:
            assert self.argsAddedToParent is not None
        else:
            while not parentArgsInfo.isComplete():
                parentArgsInfo = parentArgsInfo.parentAI()
            self.argsAddedToParent = set(self.getArgs()).difference(parentArgsInfo.getArgs())


    def isComplete(self) -> bool:
        return self.argsSpecType == self.SPEC_COMPLETE

    def getArgs(self) -> List[str]:
        return self.allOptional + self.allRequired

    def numArgs(self) -> int:
        return len(self.allOptional) + len(self.allRequired)

    def getReqdArgs(self) -> List[str]:
        return self.allRequired

    def getOptArgs(self) -> List[str]:
        return self.allOptional

    def getArgsDocs(self) -> ArgsDocs:
        return self.allDocs.copy()

    def setArgsDocs(self, docs: ArgsDocs):
        """docs is a mapping from arg names to their documentation"""
        if not self.isComplete():
            raise RuntimeError('Topic MDS is not complete, cannot set docs!')
        for arg, doc in docs.items():
            self.allDocs[arg] = doc

    def check(self, msgData: MsgData):
        """
        Check that the message arguments given satisfy the topic message
        data specification (MDS).
        :param msgData: the topic message data to check for validity
        :raise SenderMissingReqdMsgDataError: if some required args are missing or not known
        :raise SenderUnknownMsgDataError: if some optional args are unknown.
        """
        all = set(msgData)
        # check that it has all required args
        needReqd = set(self.allRequired)
        hasReqd = (needReqd <= all)
        if not hasReqd:
            raise SenderMissingReqdMsgDataError(
                self.topicNameTuple, list(msgData.keys()), needReqd - all)

        # check that all other args are among the optional spec
        optional = all - needReqd
        ok = (optional <= set(self.allOptional))
        if not ok:
            raise SenderUnknownMsgDataError(self.topicNameTuple,
                                            list(msgData.keys()), optional - set(self.allOptional))

    def filterArgs(self, msgData: MsgData) -> MsgData:
        """
        Returns a dict which contains only those items of msgData which are defined for topic.
        E.g. if msgData is {a:1, b:'b'} and topic arg spec is ('a',) then return {a:1}. The returned
        dict is valid only if check(msgData) was called (or check(superset of msgData) was called).

        :param msgData: the topic message data to filter
        """
        assert self.isComplete()
        if len(msgData) == self.numArgs():
            return msgData

        # only keep the keys from msgData that are also in topic's kwargs
        # method 1: SLOWEST
        # newKwargs = dict( (k,msgData[k]) for k in self.__msgArgs.allOptional if k in msgData )
        # newKwargs.update( (k,msgData[k]) for k in self.__msgArgs.allRequired )

        # method 2: FAST:
        # argNames = self.__msgArgs.getArgs()
        # newKwargs = dict( (key, val) for (key, val) in msgData.iteritems() if key in argNames )

        # method 3: FASTEST:
        argNames = set(self.getArgs()).intersection(msgData)
        newKwargs = dict((k, msgData[k]) for k in argNames)

        return newKwargs

    def hasSameArgs(self, *argNames: Seq[str]) -> bool:
        """
        Returns true if self has all the message arguments given, no
        more and no less. Order does not matter. So if getArgs()
        returns ('arg1', 'arg2') then self.hasSameArgs('arg2', 'arg1')
        will return true.
        """
        return set(argNames) == set(self.getArgs())

    def hasParent(self, argsInfo: ArgsInfo) -> bool:
        """return True if self has argsInfo object as parent"""
        return self.parentAI() is argsInfo

    def getCompleteAI(self) -> ArgsInfo:
        """
        Get the closest arg spec, starting from self and moving to parent,
        that is complete. So if self.isComplete() is True, then returns self,
        otherwise returns parent (if parent.isComplete()), etc.
        """
        AI = self
        while AI is not None:
            if AI.isComplete():
                return AI
            AI = AI.parentAI()  # dereference weakref
        return None

    def updateAllArgsFinal(self, topicDefn: ArgSpecGiven):
        """
        This can only be called once, if the construction was done
        with ArgSpecGiven.SPEC_GIVEN_NONE
        """
        assert not self.isComplete()
        assert topicDefn.isComplete()
        self.__setAllArgs(topicDefn)

    def __addChildAI(self, childAI: ArgsInfo):
        assert childAI not in self.childrenAI
        self.childrenAI.append(childAI)

    def __notifyParentCompleted(self):
        """Parent should call this when parent ArgsInfo has been completed"""
        assert self.parentAI().isComplete()
        if self.isComplete():
            # verify that our spec is compatible with parent's
            self.__validateArgsToParent()
            self.argsAddedToParent = set(self.getArgs()).difference(self.parentAI().getArgs())
        else:
            for argsInfo in self.childrenAI:
                argsInfo.__notifyAncestorCompleted(self.parentAI())

    def __notifyAncestorCompleted(self, parentAI):
        if self.isComplete():
            # verify that our spec is compatible with parent's
            self.__validateArgsToParent()
            self.argsAddedToParent = set(self.getArgs()).difference(parentAI.getArgs())
        else:
            for argsInfo in self.childrenAI:
                argsInfo.__notifyAncestorCompleted(parentAI)

    def __validateArgsToParent(self):
        # validate relative to parent arg spec
        closestParentAI = self.parentAI().getCompleteAI()
        if closestParentAI is not None:
            # verify that parent args is a subset of spec given:
            topicName = stringize(self.topicNameTuple)
            verifySubset(self.getArgs(), closestParentAI.getArgs(), topicName)
            verifySubset(self.allRequired, closestParentAI.getReqdArgs(), topicName, ' required args')

    def __setAllArgs(self, specGiven: ArgSpecGiven):
        assert specGiven.isComplete()
        self.allOptional = tuple(specGiven.getOptional())
        self.allRequired = specGiven.reqdArgs
        self.allDocs = specGiven.argsDocs.copy()  # doc for each arg
        self.argsSpecType = self.SPEC_COMPLETE

        parentArgsInfo = self.parentAI()
        if parentArgsInfo is None:
            self.argsAddedToParent = []
        else:
            self.__validateArgsToParent()
            while not parentArgsInfo.isComplete():
                parentArgsInfo = parentArgsInfo.parentAI()
            self.argsAddedToParent = set(self.getArgs()).difference(parentArgsInfo.getArgs())

        # notify our children
        for childAI in self.childrenAI:
            childAI.__notifyParentCompleted()
