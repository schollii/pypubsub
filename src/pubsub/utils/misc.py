"""
Provides useful functions and classes. Most useful are probably
printTreeDocs and printTreeSpec.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

import sys

__all__ = ('printImported', 'Callback')


def printImported():
    """Output a list of pubsub modules imported so far"""
    ll = [mod for mod in sys.modules.keys() if mod.find('pubsub') >= 0]  # iter keys ok
    ll.sort()
    print('\n'.join(ll))


class Callback:
    """
    This can be used to wrap functions that are referenced by class
    data if the data should be called as a function. E.g. given
    >>> def func(): pass
    >>> class A:
    ....def __init__(self): self.a = func
    then doing
    >>> boo=A(); boo.a()
    will fail since Python will try to call a() as a method of boo,
    whereas a() is a free function. But if you have instead
    "self.a = Callback(func)", then "boo.a()" works as expected.
    """

    def __init__(self, callable_obj):
        self.__callable = callable_obj

    def __call__(self, *args, **kwargs):
        return self.__callable(*args, **kwargs)
