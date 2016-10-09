"""
This module hides the source of implementation of weak method. WeakMethod is provided in pypubsub 4.0+ by either
standard lib (Python >= 3.4) or weakrefmethod (Python < 3.4). Prior to pypubsub 4.0, WeakMethod was a custom
class that adhered to the WeakRef API. Note that methods cannot be given to weakref.WeakRef because methods
cannot be referenced, only a temporary "instance method" created for each reference can be used. This would cause
WeakRef(method) to be "dead on creation".

Use the getWeakRef(object) module function to create the
proper type of weak reference (weakref.WeakRef or WeakMethod) for given object.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.

"""

# for function and method parameter counting:
from inspect import ismethod
# for weakly bound methods:
from weakref import ref as WeakRef
# WeakMethod was introduced in Python 3.4 but the weakrefmethod pypi module is a backport of it to earlier versions
try:
    from weakref import WeakMethod
except:
    from weakrefmethod import WeakMethod
# type hinting:
from typing import Tuple, List, Sequence, Mapping, Dict, Callable, Any, Optional, Union, TextIO


WeakObjOrMethod = Union[WeakMethod, WeakRef]

DeadRefObserver = Callable[[WeakObjOrMethod], None]


def getWeakRef(obj, notifyDead: DeadRefObserver = None):
    """
    Get a weak reference to obj. If obj is a bound method, a WeakMethod
    object, that behaves like a WeakRef, is returned; if it is
    anything else a WeakRef is returned. If obj is an unbound method,
    a ValueError will be raised.
    """
    if ismethod(obj):
        createRef = WeakMethod
    else:
        createRef = WeakRef

    return createRef(obj, notifyDead)
