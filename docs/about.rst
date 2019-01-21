About 
=====

.. contents:: In this section:
   :depth: 1
   :local:

License
-------

Simplified BSD:

.. literalinclude:: ../src/pubsub/LICENSE_BSD_Simple.txt


Authors
-------

The main developer of the package is Oliver Schoenborn, but Robb Shecter 
started it all back in early 2000's. The code is now hosted on
github at http://github.com/schollii/pypubsub (previous to that, it was
hosted on SourceForge.net, and prior to that, it was hosted in wxPython).
PyPubSub is on the Python Package Index at http://pypi.python.org/pypi/PyPubSub.

As listed in the :ref:`label-contributing` section, contributions of any
form are welcome. Even questions help progress the project.

:author: Oliver Schoenborn <schoenborno at (@) users.sf.net>


Acknowledgements
----------------

Thanks to SourceForge.net for hosting the project until September 2016.
Thanks to Github.com for hosting the project from October 2016.
Thanks to Robb Shecter for having
given me the chance to take over this project from him many years ago (ca 2004!).
Thanks to all those users of PyPubSub who ask questions, make suggestions, point out
bugs, etc. 


PyPubSub Users
--------------

The page at https://libraries.io/pypi/PyPubSub has useful statics on which other github
projects use/watch/fork pypubsub.

In addition, several users have donated a bit of their time to describe how they use/d
PyPubSub in their Python projects.

*Darin Gordon, for Yosai, since 2015*:
    Yosai (https://github.com/YosaiProject) is a security framework for python
    applications, offering authentication,
    authorization, and session management from a common API.  Yosai uses PyPubSub to
    facilitate event-driven responses to security-related changes.  For instance,
    when a session expires, valuable information is logged and cached authorization
    info is cleared.


*Jerome Laheurte, for Task Coach, since Feb 2012*:
    Task Coach (https://sourceforge.net/projects/taskcoach/) is a 
    simple open source todo manager to keep track of personal 
    tasks and todo lists. It is designed for composite tasks, and also offers 
    effort tracking, categories, notes and more. Task Coach uses PyPubSub as
    its Publisher/Listener implementation to cleanly separate model and view 
    layers. 


*Steven Sproat, for Whyteboard, since Feb 2010*:
    I've been using PyPubSub for around 2 months in my cross-platform
    drawing application, Whyteboard (http://launchpad.net/whyteboard). My
    Shape models (rectangle, polygons etc) use PyPubSub to notify the GUI of
    any changes to themselves or to request actions be performed on the
    canvas (e.g capture user's mouse), and the GUI responds by updating
    various dialogs with this information. This means that my shapes no
    longer need to maintain references to the canvas in order to perform
    operations on it, and can instead send a message saying "do something"
    without caring how it's done.


*Josh English, for WMS, since 2008*:
    I use it in my Writing Management System (http://joshua.r.english
    .googlepages.com/wms). I'm using it to control interfaces, such
    as telling the frame to change the status bar, or a notebook to
    change a panel. PyPubSub enables me to focus on *what* data
    to pass around my application, rather than *how* to pass it around.
    This makes it easy to put in the finer details of my application.


*Geoff Gilmour-Taylor, since April 2008*:
    I use wx.lib.pubsub for a suite of in-house batch conversion tools for
    DAISY talking books, called Garden Tools (in-house software for the CNIB
    Library, http://www.cnib.ca/en/Services/library/). For MVC,
    communication in a wxPython app.

    Loose coupling of business logic and GUI. It allows me to trigger
    multiple actions on a single message without having to locate and modify
    all the places where the message is sent. I was able to add a logging
    module that reads the same status messages that are sent to the GUI
    without having to modify any of my other code.


*Phil Mayes, for Listomax, since 2007*:
    Listomax (http://www.listomax.com/) uses version 1 of PyPubSub for MVC:
    multiple View (UI) components may need to change when the Model
    changes; simpler than direct calls, lower coupling.


*Mike Driscoll, for PyTimesheet and Zimbra Alerts, since 2007*:
    I use wx.lib.pubsub in two internal projects at my employer's business,
    "PyTimesheet" and the "Zimbra Alerts". I use it to send information
    between various frames, such as an options menu back to the main
    application that launched it. The main application I use it for though
    is a Timesheet program where I use it to tell my program which frame to
    display when. Basically when one closes, I need another one to open and
    I found that PyPubSub made this quite trivial. The other program is used
    in conjunction with our Zimbra web mail and will pop-up an alert when we
    receive an email and it also has an Outlook-like Reminder dialog for
    appointments... And thanks for providing such a nice tool for my
    arsenal!


*Anthony Floyd, RAVEN, since 200?*:
    Our project is called "RAVEN", it's an analytical and finite-element
    analysis program for simulating and analyzing the processing of
    composite materials in the aerospace industry. We use PyPubSub as
    the communications backbone.  We essentially have a MVC
    framework, and use PyPubSub to have the UI respond to things happening in
    the data.  However, we also use it to have data objects respond to
    changes in other data objects.

    We're quite enamoured with PyPubSub! It's proven to be an effective way
    to keep the UI out of the backend, and an effective way to keep the
    backend modularized.


*Sebastian Zurek, OpenSynergy, since 2007*:
    I'm using wx.lib.pubsub module as part of the OpenSynergy framework
    (http://www.opensynergy.pl, temporarily offline) that I am developing,
    and I found it VERY usefull. PyPubSub is used as the communication layer
    betteen the extensions components and the framework, between the Model
    and Visual, and between the Visual elements.


*Werner F. Bruhin, for the The Wine Cellar Book, since 2006*
    Have been using PyPubSub for years and since I started work on version 4 of
    my application [http://thewinecellarbook.com)] over a year ago I switched to 
    the PyPubSub v3 API and defined a topic tree.  Having a topic tree is just
    great as you make sure that you don't mistype the topic names and on top you 
    have nice documentation on what topics you already defined and what 
    parameter(s) need to be passed for each topic.

    Currently I have topics to keep track of database state, data 
    needs saving, database item/row has changed, was deleted etc which trigger 
    updates to relevant lists to update themselves if needed and to show 
    messages on a wx.InfoBar. 


*Mike Rooney, for wxBanker, since 2006*:
    I use PyPubSub as the crucial event handling mechanism for wxBanker
    (https://launchpad.net/wxbanker). It works well for implementing design
    patterns such as MVC where you want to eliminate coupling, since it
    doesn't require that you know specific method names or implementation
    details of other classes, modules, or libraries. PyPubSub is also great
    when you want to make an announcement without requiring that anything
    (or how many things) is listening to or acting upon that announcement.
    In short, PyPubSub makes intra-process communication a dream come true.


*QVI (http://www.qvii.com/) for several applications, since 2006*:
    Here at QVI we use PyPubSub for most of our wxPython applications (notably
    SmartTree), to achieve very lightweight, simple, and readable
    communication between classes and modules. One of the nice aspects of
    PyPubSub is how easy it is to incorporate into existing code, and how
    well-suited it is for pluggable/modular designs which want to make
    announcements about events, but don't require that or care if any other
    module is listening. It makes handling "events" easy, whatever we define
    them to be, and removes the need for the handlers to have any specific
    knowledge of how the announcements are made or where they came from.

    After discovering we could use PyPubSub independently of wxPython, we also
    use it in an application or two that doesn't use wxPython at all, but
    where we still desire a lightweight event handling mechanism (when don't
    you?).


*Oliver Schoenborn (Author of PyPubSub), for several applications, from 2004 to 2010*:
    I have used PyPubSub on several projects. Applications which, for example,

    - show tree structures with selectable nodes, and selected node's
      associated information panel 
    - show objects on information panels with info regarding progress
      of other components (running on other machines) updated in 
      real time
    - show dialog boxes with with entry fields for settings
    - have several panels in a wizard style to configure a task for execution

    With PyPubSub, one event occurs due to a mouse click on an icon, and
    and all parts of the code that need updating get called with the new
    data. This means automatic update of menu items (adding, removing etc),
    state in various panels, etc. Gone are the long sequences of calls
    through the code.
    
    Last time I had to build or maintain a Python event-based
    application was 2009, but I'm dedicated to maintaining PyPubSub for other
    developers. When I make or incorporate improvements based on user 
    feedback, I rely on the high % coverage of the unit regression 
    tests, the useful examples, and the exception messages which give a 
    lot of useful information when the message data fields don't adhere to 
    the topic definition (inferred or specified). 
    
    I look forward to my next event-based Python application, which might 
    be in the fall of 2013. 


.. _label-history:

History
-------

PyPubSub was originally created by Robb Shecter as a module in the
wxPython library, named wx.lib.pubsub, sometime around y2k. At that time,
pubsub had one responsiblity: to allow for messages to be sent to listeners
based on a hierarchy of topics. In the Spring of 2004, I added the
ability to automaticaly unregister listeners that were no longer in use
outside of PyPubSub (by making the module's Publisher use weak references to
listeners). For large PyPubSub-based application, this greatly simplified
listener management. I asked Robin Dunn if he would like the changes
to be put in wx.lib.pubsub; he forwarded the request to Robb. And the rest
is history.

Only a few minor tweaks and improvements happened for the next couple years.
In 2006 when I used PyPubSub
on a couple larger projects, I wished that topic trees and the topic message
data could be documented. I also found that a major time waster when using
pubsub at that time was debugging incorrect message data, so I started thinking
of a way that I could validate message data. I also
wished that I could find a design that would allow the use
of tools like pylint to point out invalid topic names.

So I developed version 2 of wx.lib.pubsub in the
Fall of 2006. I also created an entry in the Python Package Index as PyPubSub
(http://pypi.python.org/pypi/PyPubSub) and used PyPI to hold a
snapshot of my files so that even developers not using wxPython could
benefit from it.

In May 2007 I decided it was time to create a project on SourceForge.net for it.
It was http://sourceforge.net/projects/pubsub, so the web site was at
http://pubsub.sourceforge.net. The wx.lib.pubsub was then a verbatim copy of the
src folder from sf.net/projects/pubsub, as it was before PyPubSub version 2.

In 2008 someone created, unbeknownst to me,
an unrelated Python project on sourceforge and named it PyPubSub. The author
did not realize that mine already existed with that name in PyPI and that
therefore he would have to rename his so as not to confuse users. This project
came to my attention when I wanted to rename pubsub on SF.net to pypubsub to make
it clear that it was python based, and to match the already one-year old entry on
PyPI. In the end, the author renamed his project and sf.net/projects/pypubsub
was available for my taking.

After using PyPubSub version 2 for a bit I wasn't really happy with it, so I went back
to the drawing board to support topic and message data documentation, definition and
validation started. Version 3.0.0, completed some time
in 2008, achieved this via keyword-based message data and topic definition providers.
Version 3 also added support for tracking PyPubSub activity such as listener subscription,
topic creation, and sending messages, very useful in large applications.

Version 3 of PyPubSub was not compatible with v2 or v1, so I couldn't directly upgrade
wx.lib.pubsub to it without at least supporting a deprecated v1 for a while.
This led to version 3.1.0 in early 2010, which supported the v1 API via a setupv1.py
configuration module that could be imported before the first import of pubsub.
This was quite a challenge as there was a fair bit of commonality between PyPubSub v1 and v3,
but also some significant differences. In retrospect I should not have done that because
it made the code rather complex. I did a good job of it so it was easy to make fixes, but
it could be a pain to troubleshoot. If I had to walk the same mile again, I would
just have two separate implementations, with an easy way to import one or the other
(e.g. pubsub vs pubsub3 package package folders).

Not much happened between early 2010 and first half of 2013, except for a minor
release 3.1.2 in November 2011: the code was stable and did its job nicely so no 
major changes needed. Also in that period I didn't develop or maintain any 
event-based Python application so I didn't have any reason to update PyPubSub. I
did accumulate about a dozen tickets on SF.net involving minor bugs or patches
contributed by users in that period. 

The overhaul of wxPython 'Phoenix' in 2013 was the perfect opportunity to make
pubsub version 3 API the default, and to make version 1 API accessible only on demand
(via the setuparg1.py configuration module).
I also removed all the code that was there just to support the old
version 1 API, leaving just a version 3 API with two message protocols available.
I took the opportunity to address the dozen tickets during the
summer of 2013, and to improve the docs.

In early 2016 I started work to remove the deprecated code and support only the
original messaging protocol that I had designed in 3.0. With two busy kids,
it is not easy to find the time to do this, so it took me till October 2016 for me to
get my act together and finally release v4: a nice simple design with no import
magic needed, no configuration, no complicated docs to explain the mulitple APIs,
use of wheels instead of eggs, use of annotations, etc.


.. _label-roadmap:

Roadmap
-------

List of things I would like to add to PyPubSub:

- complete implementation of multi-threading helper class, no change
  required to PyPubSub, rather just utility class to help user
  (pseudo-code already in src/contrib)
- figure out a good way to prevent wrapped listener subscriptions from being DOA
  (PyPubSub only keeps weak reference to listener, so if listener subscribe like
  ``pub.subscribe( wrapper(yourListener) )`` then listener will be unsubscribed
  as soon as subscribe returns; you need
  ``refListener = wrapper(yourListener); pub.subscribe(refListener)``)
- finish the src/contrib/monitor implementation to monitor PyPubSub messages,
  or some way of monitoring message sending

If anyone is interested in helping, please post on the dev forum.

The following is no longer on list of things to do:

- support pubsub over UDP and TCP sockets: mqtt does this! PyPubSub and mqtt
  are complementary: PyPubSub for messaging between application components within
  one Python interpreter; mqtt for messaging between compoonents on a network.

