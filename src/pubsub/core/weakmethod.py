"""
This module hides the source of implementation of weak ref to a method: for Python 3.4, it is
Python's weakref module; for earlier Python, it is the weakrefmethod module from PyPI.
Prior to pypubsub 4.0, WeakMethod was a custom class that adhered to the WeakRef API.

Use the getWeakRef(object) module function to create the
proper type of weak reference (weakref.WeakRef or WeakMethod) for given object.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

from inspect import ismethod
from weakref import ref as WeakRef

# for weakly bound methods:
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
