"""
Miscellaneous utility items

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

from typing import Any


def annotationType(sig_obj: Any):
    """
    Use to forward declare an annotation type, i.e. a type that will be fully defined later but is not available
    at the annotation location in the source code. The following example shows a MyType class with a method that
    accepts a MyType instance; annotating this cannot be done in Python::

        class MyType:
            def copy_from(other: MyType):  # interpreter will croak
                ...

    The recommended approach is to use a string annotation, but this is rather unnatural in Python code::

        class MyType:
            def copy_from(other: 'MyType'):
                ...

    The annotationType function allows a more pythonic syntax:

        @annotationType
        class MyType:
            pass

        class MyType:
            def copy_from(other: MyType):
                ...

    This decorator doesn't actually do anything to its argument.
    """
    return sig_obj
