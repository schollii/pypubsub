How Tos
=======

This section provides "recipes" for various tasks such as migrating an 
application from one PyPubSub version or messaging protocol to another.


.. _label-migrations:

Migrations
----------

In the very first version of PyPubSub, v1, message data was transported via a
single instance of a class called Message. This would later get called the "arg1"
messaging protocol API. The implementation had several 
important limitations, most importantly the inability to validate whether 
the correct data fields were being included in a message sent. For larger
applications, this made debugging more tedious than it ought to be. This 
version of PyPubSub is no longer supported and does not exist in source
form.

PyPubSub v2 had a short life as it was more of an experiment; it does not 
exist in source form, not even in a VCS -- the data was lost during migration
from SourceForge to github. If you somehow have that version and need help
migrating from it to v3 or v4, post on github. 

In PyPubSub v3, a new messaging protocol was added to address shortcomings
of arg1: it was named kwargs since it was based on Python's support for keyword
arguments. This made it possible for those using v1 to move to v3: just change
a couple of lines of code to satisfy the updated pypubsub API, including a
line that "configured" PyPubSub to use the arg1 protocol. The v3 of PyPubSub 
also included, as a temporary measure, some helper functions to support a 
step-wise transition from arg1 to the kwargs protocol possible. The v3 of 
PyPubSub had of course many improvements related to debugging message passing.
PyPubSub 3.3 was compatible with both Python 2.7 and 3.4+. 

PyPubSub v4 dropped support for arg1 protocol, and Python 2.7, entirely. This 
drammatically simplified the code base, and allowed to make use of Python 
annotations (type hinting), and a few other niceties related to introspection, 
Paths, enums, etc. 

To upgrade your application from PyPubSub's arg1 messaging protocol to the 
kwargs protocol, you must do the following: 

- Install PyPubSub 3.3 from pypi (``pip install pypubsub==3.3``); then use 
  the docs there to perform a step-wise migration to kwargs (see )
- Once that is done and all your tests pass (you *do* have unit tests, right?),
  the next step depends on which version of Python you use: 
  
  - Python 2.7: Install PyPubSub 3.4.
  - Python 3.3+: Install PyPubSub 4.x.
  
  There should be no further changes necessary when doing either of the above. 

Please post on the list or github for any additional support needed on this 
topic.
