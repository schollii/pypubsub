"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import gc

from nose.tools import (
    assert_raises, 
    assert_equal, 
    assert_not_equal, 
    assert_true,
)

# in python 2.6, nose does not have all assert_ functions
try:
    from nose.tools import (
        assert_is_none,
        assert_is_not_none,
    )
except ImportError:
    def assert_is_none(exp, msg=None):
        return assert_true(exp is None, msg)
    def assert_is_not_none(exp, msg=None):
        return assert_true(exp is not None, msg)

# ok no for the actual pubsub code imports
from pubsub import py2and3

from pubsub.core.weakmethod import WeakMethod
from pubsub.core import listener
from pubsub.core.listener import (
    Listener, ListenerValidator,
    ListenerMismatchError,
    CallArgsInfo,
    getArgs,
)

def test0_ArgsInfo():
    def listener0(msgTopic = Listener.AUTO_TOPIC): pass
    CallArgsInfo(listener0, 0)

    def listener1(arg1, msgTopic = Listener.AUTO_TOPIC): pass
    CallArgsInfo(listener1, 1)
    

class ArgsInfoMock:
    def __init__(self, autoTopicArgName=None):
        self.autoTopicArgName = autoTopicArgName
        self.acceptsAllKwargs = False
        

def test2_Validation0():
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
    assert_raises(ListenerMismatchError, validate, extraArg)   # E: extra arg
    assert_raises(ListenerMismatchError, validate, extraKwarg) # E: extra kwarg

def test2_Validation1():
    # one arg/kwarg in topic
    validator = ListenerValidator(['a'], ['b'])
    validate = validator.validate

    def same(a, b=1): pass
    def same2(a=2, b=1): pass
    def varkwargs(**kwargs): pass
    def varkwargs_a(a, **kwargs): pass

    def opt_reqd(b, **kwargs): pass
    def missing_arg(b=1): pass
    def missing_kwarg(a): pass
    def extra_kwarg1(a,b=1,c=2): pass
    def extra_kwarg2(c=1, *args, **kwargs): pass
    def extra_arg1(a,c,b=1): pass
    def extra_arg2(a,b,c=2): pass

    validate(same)           # ok: same
    validate(same2)          # ok: same even if a now has default value
    validate(varkwargs_a)    # ok: has **kwargs
    validate(varkwargs)    # ok: has **kwargs

    assert_raises( ListenerMismatchError, validate, opt_reqd)      # E: b now required
    assert_raises( ListenerMismatchError, validate, missing_arg)   # E: missing arg
    assert_raises( ListenerMismatchError, validate, missing_kwarg) # E: missing kwarg
    assert_raises( ListenerMismatchError, validate, extra_kwarg1)  # E: extra kwarg
    assert_raises( ListenerMismatchError, validate, extra_kwarg2)  # E: extra kwarg
    assert_raises( ListenerMismatchError, validate, extra_arg1)    # E: extra arg
    assert_raises( ListenerMismatchError, validate, extra_arg2)    # E: extra arg


def test3_IsCallable():
    # Test the proper trapping of non-callable and certain types of
    # callable objects.

    # validate different types of callables
    validator = ListenerValidator([], [])
    # not a function:
    notAFunc = 1 # just pick something that is not a function
    assert_raises(ListenerMismatchError, validator.validate, notAFunc)
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
    

def test4_WantTopic():
    # Test the correct determination of whether want topic
    # auto-passed during sendMessage() calls.

    # first check proper breakdown of listener args:
    def listener(a, b=1): pass
    argsInfo = CallArgsInfo(listener, 0)
    assert_equal( None, argsInfo.autoTopicArgName )

    msgTopic = 'auto'
    class MyListener:
        def method(self, a, b=1, auto=Listener.AUTO_TOPIC): pass
    listener = MyListener()
    argsInfo = getArgs(listener.method)
    assert_equal( msgTopic, argsInfo.autoTopicArgName )
    assert_equal( ['a','b'], argsInfo.allParams )

    # now some white box testing of validator that makes use of args info:
    def checkWantTopic(validate, listener, wantTopicAsArg=None):
        argsInfo = getArgs(listener)
        assert_equal(argsInfo.autoTopicArgName, wantTopicAsArg)
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
    
def test5a_weakref():
    from weakref import ref as weakref
    from inspect import isfunction, ismethod
    
    class Foo:
        def instanceMethod(self): pass
        @classmethod
        def classMethod(cls): pass
        def __call__(self): pass
        
    if py2and3.PY2:    
        assert_true( ismethod(Foo.instanceMethod) )
        wr = weakref(Foo.instanceMethod)
        gc.collect() # for pypy: the gc doesn't work the same as cpython's
        assert_is_none(wr(), 'Foo.instanceMethod')
    else:
        assert_true( isfunction(Foo.instanceMethod) )
        wr = weakref(Foo.instanceMethod)
        assert_is_not_none(wr(), 'Foo.instanceMethod')

    assert_true( ismethod(Foo.classMethod) )
    wr = weakref(Foo.classMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_is_none(wr(), 'Foo.classMethod')

    foo = Foo()
    fooWR = weakref(foo)
    assert_is_not_none(fooWR(), 'foo')

    assert_true( ismethod(foo.instanceMethod) )
    wr = weakref(foo.instanceMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_is_none(wr(), 'foo.instanceMethod') 
    
    assert_true( ismethod(foo.classMethod) )
    wr = weakref(foo.classMethod)
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_is_none(wr(), 'foo.classMethod')

    del foo
    gc.collect()
    assert_is_none(fooWR(), 'foo')
    
def test5_DOAListeners_1(): 
    # Test "dead on arrival"

    # test DOA of unbound method
    def getListener1():
        class DOA:
            def tmpFn(self): pass
        return Listener( DOA.tmpFn, ArgsInfoMock() )
        
    if py2and3.PY2:
        assert_raises(ValueError, getListener1)
    else:
        unbound = getListener1()
        assert not unbound.isDead()

        
def test5_DOAListeners_2(): 
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
    assert_raises(RuntimeError, doa1, None, {})

    # check dead-on-arrival when a death callback specified:
    doa2 = Listener( Wrapper(fn), ArgsInfoMock(), onDead )
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert doa2.getCallable() is None
    assert doa2.isDead()
    assert_raises(RuntimeError, doa2, None, {})


def test6_ListenerEq():
    # Test equality tests of two listeners

    def listener1(): pass
    def listener2(): pass
    l1 = Listener(listener1, ArgsInfoMock())
    l2 = Listener(listener2, ArgsInfoMock())
    # verify that Listener can be compared for equality to another Listener, weakref, or callable
    assert_equal    ( l1, l1 )
    assert_not_equal( l1, l2 )
    assert_equal    ( l1, listener1 )
    assert_not_equal( l1, listener2 )
    ll = [l1]
    assert listener1 in ll
    assert listener2 not in ll
    assert_equal( ll.index(listener1), 0 )
    
    # now for class method listener:
    class MyListener:
        def __call__(self): pass
        def meth(self): pass
    listener3 = MyListener()
    l3 = Listener(listener3, ArgsInfoMock() )
    assert_not_equal( l3, l1 )
    assert_not_equal( l3, l2 )
    assert_not_equal( l3, listener2 )
    assert_equal    ( l3, l3 )
    assert_equal    ( l3, listener3 )
    assert_not_equal( l3, listener3.__call__ )

    l4 = Listener(listener3.meth, ArgsInfoMock() )
    assert_equal    ( l4, l4 )
    assert_not_equal( l4, l3 )
    assert_not_equal( l4, l2 )
    assert_not_equal( l4, listener3.__call__ )
    assert_equal    ( l4, listener3.meth )

    
def test7_DyingListenersClass():
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
    assert_equal( len(lsrs), 3 )
    del listener1
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_equal( len(lsrs), 2 )
    assert_equal( lsrs[0], listener2 )
    assert_equal( lsrs[1], listener3 )
    del listener2
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_equal( len(lsrs), 1 )
    assert_equal( lsrs[0], listener3 )
    del listener3
    gc.collect() # for pypy: the gc doesn't work the same as cpython's
    assert_equal( len(lsrs), 0 )
    

def test8_getArgsBadListener():
    assert_raises( ListenerMismatchError, getArgs, 1)
    try:
        getArgs(1)
    except ListenerMismatchError:
        from pubsub import py2and3
        exc = py2and3.getexcobj()
        msg = 'Listener "int" (from module "__main__") inadequate: type "int" not supported'
        assert_equal( str(exc), msg )


def test10_weakMethod():
    class Foo:
        def meth(self): pass
    foo = Foo()
    wm = WeakMethod(foo.meth)
    str(wm)


def test11_testNaming():
    aiMock = ArgsInfoMock()

    # define various type of listeners
    def fn(): pass
    class Foo:
        def __call__(self): pass
        def meth(self): pass

    ll = Listener(fn, aiMock)
    assert_equal( ll.typeName(), "fn")
    assert_equal( ll.module(), "test1_listener")
    assert not ll.wantsTopicObjOnCall()
    
    foo = Foo()
    ll = Listener(foo, aiMock)
    assert_equal( ll.typeName(), "Foo")
    assert_equal( ll.module(), "test1_listener")
    assert not ll.wantsTopicObjOnCall()

    ll = Listener(foo.meth, ArgsInfoMock('argName'))
    assert_equal( ll.typeName(), "Foo.meth")
    assert_equal( ll.module(), "test1_listener")
    assert ll.wantsTopicObjOnCall()


