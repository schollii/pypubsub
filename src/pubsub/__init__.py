"""
Pubsub package initialization.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE_BSD_Simple.txt for details.
"""

# Version is provided by setuptools_scm at build time via src/pubsub/_version.py
try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover - fallback for editable installs without SCM metadata
    __version__ = "0.0.0"

__all__ = [
    'pub',
    'utils',
    '__version__'
]
