.. image:: https://badge.fury.io/py/Pypubsub.svg
    :target: https://badge.fury.io/py/Pypubsub
.. image:: https://github.com/schollii/pypubsub/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/schollii/pypubsub/actions/workflows/ci.yml
    
News
====

- January 2019: pypubsub 4.0.3 released! (for those -- and only those -- who use Python >= 3).
- March 2019: pypubsub 3.4.2 released (for those -- and only those -- who use Python 2.7.x).

Overview
========

Provides a publish-subscribe API to facilitate event-based or message-based
architecture in a single-process application. It is pure Python and works on
Python 3.7+ (tested through 3.14). It is centered on the notion of a topic; senders publish
messages of a given topic, and listeners subscribe to messages of a given
topic, all inside the same process. The package also supports a variety of
advanced features that facilitate debugging and maintaining topics
and messages in larger desktop- or server-based applications.

Install most recent stable with "pip install pypubsub".

Useful links:

- Project on PyPI: https://pypi.python.org/pypi/PyPubSub
- The documentation for latest stable release is at
  http://pypubsub.readthedocs.io.
- The documentation for latest code is at
  http://pypubsub.readthedocs.io/en/latest.

Contributing and testing
------------------------

Install `uv <https://github.com/astral-sh/uv>`_, then run the test matrix with ``tox`` (uses ``tox-uv`` under the hood)::

  uv tool install tox --with tox-uv
  tox  # or: tox -e py312

Package build verification is available via ``tox -e pkg`` (runs ``python -m build`` and ``twine check``).

Python 3.7 note: uv does not auto-provide CPython 3.7. ``tox -e py37`` will skip locally if 3.7 isn’t available; it is exercised in GitHub CI.

Local development install
-------------------------

Create a virtual environment and install in editable mode::

  uv venv .venv && source .venv/bin/activate
  uv pip install -e .

Then you can open a Python shell (``python``) and ``import pubsub``, or run examples such as::

  python examples/advanced/advanced_main.py
  python examples/basic_kwargs/console_main.py

To run a small example suite, use the helper script (assumes your venv is active)::

  bash examples/runall.sh  # uses 'python' from your venv

wxPython on Ubuntu 22+
----------------------

If you want to run the wx examples, install wxPython and SDL2 runtime in your venv on Ubuntu 22.x+::

  pip install --upgrade pip setuptools wheel
  pip install --only-binary=:all: -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython==4.2.4
  sudo apt-get install libsdl2-2.0-0  # runtime for the wheel

If the wheel is not found for your distro/Python combo, you’ll need GTK3/SDL build deps to compile from source instead.
