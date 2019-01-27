"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import gc
import sys
import pytest

from pubsub.core.weakmethod import WeakMethod
from pubsub.core import listener
from pubsub.core.listener import (
    Listener, ListenerMismatchError,
    CallArgsInfo,
    getArgs,
    ListenerValidator)


def test_ArgsInfo():
    def listener0(msgTopic = Listener.AUTO_TOPIC): pass
    CallArgsInfo(listener0)

    def listener1(arg1, msgTopic = Listener.AUTO_TOPIC): pass
    CallArgsInfo(listener1)

    def listenerWithHints(arg1, arg2, *, kwarg1, kwarg2=4, **kwargs): pass
    c = CallArgsInfo(listenerWithHints)
    assert c.acceptsAllKwargs == True
    assert c.requiredArgs == ('arg1', 'arg2', 'kwarg1')
    assert c.optionalArgs == ('kwarg2',)
    assert c.getOptionalArgs() == c.optionalArgs
    assert c.getRequiredArgs() == c.requiredArgs

    def listenerWithHints2(arg1, arg2=2, *, kwarg1, kwarg2=4, **kwargs): pass
    c = CallArgsInfo(listenerWithHints2)
    assert c.acceptsAllKwargs == True
    assert c.requiredArgs == ('arg1', 'kwarg1')
    assert c.optionalArgs == ('arg2', 'kwarg2')
    assert c.getOptionalArgs() == c.optionalArgs
    assert c.getRequiredArgs() == c.requiredArgs


class ArgsInfoMock:
    def __init__(self, autoTopicArgName=None):
        self.autoTopicArgName = autoTopicArgName
        self.acceptsAllKwargs = False


def test_Validation0():
    # Test when ValidatorSameKwargsOnly used, ie when args in
    # listener and topic must be exact match (unless *arg).
    AA = Listener.AUTO_TOPIC

    # test for topic that has no arg/kwargs in topic message spec (TMS)
    def same(): pass
    def varargs(*args, **kwargs): pass
    def autoArg(msgTopic=AA): pass
    def extraArg(a): pass
    def extraKwarg(a=1): pass

    # no arg/kwarg in topic message spec (TMS)
    validator = ListenerValidator([], [])
    validate = validator.validate

    validate(same)      # ok: same
    validate(varargs)   # ok: *args/**kwargs
    validate(autoArg)   # ok: extra but AUTO_TOPIC
    pytest.raises(ListenerMismatchError, validate, extraArg)   # E: extra arg
    validate(extraArg, curriedArgNames=('a',))  # ok: extra is curried
    validate(extraKwarg)  # ok: extra but AUTO_TOPIC

def test_Validation1():
    # one arg/kwarg in topic
    validator = ListenerValidator(['a'], ['b'])
    validate = validator.validate

    def same(a, b=1): pass
    def same2(a=2, b=1): pass
    def varkwargs(**kwargs): pass
    def varkwargs_a(a, **kwargs): pass
    def extra_kwarg1(a, b=1, c=2): pass

    def opt_reqd(b, **kwargs): pass
    def missing_arg(b=1): pass
    def missing_kwarg(a): pass
    def extra_kwarg2(*args, **kwargs): pass
    def extra_arg1(a,c,b=1): pass
    def extra_arg2(a,b,c=2): pass

    validate(same)           # ok: same
    validate(same2)          # ok: same even if a now has default value
    validate(varkwargs_a)    # ok: has **kwargs
    validate(varkwargs)      # ok: has **kwargs
    validate(extra_kwarg1)   # ok: extra arg has default value
    validate(extra_kwarg2)   # ok: can accept anything

    pytest.raises( ListenerMismatchError, validate, opt_reqd)      # E: b now required
    pytest.raises( ListenerMismatchError, validate, missing_arg)   # E: missing arg
    pytest.raises( ListenerMismatchError, validate, missing_kwarg) # E: missing kwarg
    pytest.raises( ListenerMismatchError, validate, extra_arg1)    # E: extra arg
    pytest.raises( ListenerMismatchError, validate, extra_arg2)    # E: extra arg


def test_IsCallable():
    # Test the proper trapping of non-callable and certain types of
    # callable objects.

    # validate different types of callables
    validator = ListenerValidator([], [])
    # not a function:
    notAFunc = 1 # just pick something that is not a function
    pytest.raises(ListenerMismatchError, validator.validate, notAFunc)
    # a regular function:
    def aFunc(): pass
    validator.validate(aFunc)
    # a functor and a method
    class Foo(object):
        def __call__(self): pass
        def meth(self):     pass
    foo = Foo()
    validator.validate(foo)
    validator.validate(foo.meth)


def test_WantTopic():
    # Test the correct determination of whether want topic
    # auto-passed during sendMessage() calls.

    # first check proper breakdown of listener args:
    def listener(a, b=1): pass
    argsInfo = CallArgsInfo(listener)
    assert None == argsInfo.autoTopicArgName

    msgTopic = 'auto'

    class MyListener:
        def method(self, a, b=1, auto=Listener.AUTO_TOPIC): pass

    listener = MyListener()
    argsInfo = getArgs(listener.method)
    assert msgTopic == argsInfo.autoTopicArgName
    assert ('a','b') == argsInfo.allParams

    class MyFunctor:
        def __call__(self, a, b=1, auto=Listener.AUTO_TOPIC): pass

    listener = MyFunctor()
    argsInfo = getArgs(listener)
    assert msgTopic == argsInfo.autoTopicArgName
    assert ('a','b') == argsInfo.allParams

    # now some white box testing of validator that makes use of args info:
    def checkWantTopic(validate, listener, wantTopicAsArg=None):
        argsInfo = getArgs(listener)
        assert argsInfo.autoTopicArgName == wantTopicAsArg
        validate(listener)

    validator = ListenerValidator([], ['a'])
    validate = validator.validate
    def noWant(a=1): pass
    def want1(a=1, auto=Listener.AUTO_TOPIC): pass
    checkWantTopic(validate, noWant)
    checkWantTopic(validate, want1, msgTopic)

    validator = ListenerValidator(['a'], ['b'])
    validate = validator.validate
    def noWant2(a, b=1): pass
    def want2(a, auto=Listener.AUTO_TOPIC, b=1): pass
    checkWantTopic(validate, noWant2)
    checkWantTopic(validate, want2, msgTopic)

    # topic that has Listener.AUTO_TOPIC as an arg rather than kwarg
    validator = ListenerValidator([msgTopic], ['b'])
    validate = validator.validate
    def noWant3(auto, b=1): pass
    checkWantTopic(validate, noWant3)

def test_weakref():
    from weakref import ref as weakref
    from inspect import isfunction, ismethod

    class Foo:
        def instanceMethod(self): pass
        @classmethod
        def classMethod(cls): pass
        def __call__(self): pass

    assert isfunction(Foo.instanceMethod)
    wr = weakref(Foo.instanceMethod)
    assert wr() is not None, 'Foo.instanceMethod'

    assert ismethod(Foo.classMethod)
    wr = weakref(Foo.classMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert wr() is None, 'Foo.classMethod'

    foo = Foo()
    fooWR = weakref(foo)
    assert fooWR() is not None, 'foo'

    assert ismethod(foo.instanceMethod)
    wr = weakref(foo.instanceMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert wr() is None, 'foo.instanceMethod'

    assert ismethod(foo.classMethod)
    wr = weakref(foo.classMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert wr() is None, 'foo.classMethod'

    del foo
    gc.collect()
    assert fooWR() is None, 'foo'


def test_DOAListeners_1():
    # Test "dead on arrival"

    # test DOA of unbound method
    def getListener1():
        class DOA:
            def tmpFn(self): pass
        return Listener( DOA.tmpFn, ArgsInfoMock() )

    unbound = getListener1()
    assert not unbound.isDead()


def test_DOAListeners_2():
    # test DOA of tmp callable:
    def fn():
        pass
    class Wrapper:
        def __init__(self, func):
            self.func = func
        def __call__(self):
            pass
    def onDead(listenerObj):
        pass

    # check dead-on-arrival when no death callback specified:
    doa1 = Listener( Wrapper(fn), ArgsInfoMock() )
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert doa1.getCallable() is None
    assert doa1.isDead()
    pytest.raises(RuntimeError, doa1, None, {})

    # check dead-on-arrival when a death callback specified:
    doa2 = Listener( Wrapper(fn), ArgsInfoMock(), onDead )
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert doa2.getCallable() is None
    assert doa2.isDead()
    pytest.raises(RuntimeError, doa2, None, {})


def test_ListenerEq():
    # Test equality tests of two listeners

    def listener1(): pass
    def listener2(): pass
    l1 = Listener(listener1, ArgsInfoMock())
    l2 = Listener(listener2, ArgsInfoMock())
    # verify that Listener can be compared for equality to another Listener, weakref, or callable
    assert l1 == l1
    assert l1 != l2
    assert l1 == listener1
    assert l1 != listener2
    ll = [l1]
    assert listener1 in ll
    assert listener2 not in ll
    assert ll.index(listener1) == 0

    # now for class method listener:
    class MyListener:
        def __call__(self): pass
        def meth(self): pass
    listener3 = MyListener()
    l3 = Listener(listener3, ArgsInfoMock() )
    assert l3 != l1
    assert l3 != l2
    assert l3 != listener2
    assert l3 == l3
    assert l3 == listener3
    assert l3 != listener3.__call__

    l4 = Listener(listener3.meth, ArgsInfoMock() )
    assert l4 == l4
    assert l4 != l3
    assert l4 != l2
    assert l4 != listener3.__call__
    assert l4 == listener3.meth


def test_DyingListenersClass():
    # Test notification callbacks when listener dies

    # test dead listener notification
    def onDead(weakListener):
        lsrs.remove(weakListener)

    def listener1(): pass
    def listener2(): pass
    def listener3(): pass
    lsrs = []
    lsrs.append( Listener(listener1, ArgsInfoMock(False), onDead=onDead) )
    lsrs.append( Listener(listener2, ArgsInfoMock(False), onDead=onDead) )
    lsrs.append( Listener(listener3, ArgsInfoMock(False), onDead=onDead) )

    # now force some listeners to die, verify lsrs list
    assert len(lsrs) == 3
    del listener1
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert len(lsrs) == 2
    assert lsrs[0] == listener2
    assert lsrs[1] == listener3
    del listener2
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert len(lsrs) == 1
    assert lsrs[0] == listener3
    del listener3
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert len(lsrs) == 0


def test_getArgsBadListener():
    pytest.raises( ListenerMismatchError, getArgs, 1)
    try:
        getArgs(1)
    except ListenerMismatchError:
        exc = sys.exc_info()[1]
        msg = 'Listener "int" (from module "__main__") inadequate: type "int" not supported'
        assert str(exc) == msg


def test_weakMethod():
    class Foo:
        def meth(self): pass
    foo = Foo()
    wm = WeakMethod(foo.meth)
    str(wm)


def test_testNaming():
    aiMock = ArgsInfoMock()

    # define various type of listeners
    def fn(): pass
    class Foo:
        def __call__(self): pass
        def meth(self): pass

    ll = Listener(fn, aiMock)
    assert ll.typeName() == "fn"
    assert ll.module() == "test1_listener"
    assert not ll.wantsTopicObjOnCall()

    foo = Foo()
    ll = Listener(foo, aiMock)
    assert ll.typeName() == "Foo"
    assert ll.module() == "test1_listener"
    assert not ll.wantsTopicObjOnCall()

    ll = Listener(foo.meth, ArgsInfoMock('argName'))
    assert ll.typeName() == "Foo.meth"
    assert ll.module() == "test1_listener"
    assert ll.wantsTopicObjOnCall()


def test_call():
    aiMock = ArgsInfoMock()
    result = []

    def fn(a, b, c=1, d=2, **e):
        result.append((a,b,c,d,e))

    listener = Listener(fn, aiMock)
    listener(dict(a=123, b=456), 'test_topic')
    assert result[0] == (123, 456, 1, 2, {})

    listener = Listener(fn, aiMock, curriedArgs=dict(b=4, d=5, f=6))
    listener(dict(a=123), 'test_topic')
    assert result[1] == (123, 4, 1, 5, {'f': 6})
