About 
======

.. contents:: In this section:
   :depth: 1
   :local:

License
--------

Simplified BSD:

.. literalinclude:: ../src/pubsub/LICENSE_BSD_Simple.txt


Authors
-----------

The main developer of the package is Oliver Schoenborn, but Robb Shecter 
started it all back in early 2000's. The code is now hosted on
SourceForge.net at http://www.sf.net/projects/pubsub, and has an entry
in Cheeseshop at http://pypi.python.org/pypi/PyPubSub.

As listed in the :ref:`label-contributing` section, contributions of any
form are welcome. Even questions help progress the project.

:author: Oliver Schoenborn <schoenborno at (@) users.sf.net>


Acknowledgements
----------------

Thanks to SourceForge.net for hosting the project, to Robb Shechter to have 
given me the chance to take over this project from him many years ago, to 
all those users of pubsub who ask questions, make suggestions, point out 
bugs, etc. 

.. image:: http://sflogo.sourceforge.net/sflogo.php?group_id=197063&amp;type=2
   :alt: SourceForge.net Logo
   :width: 125
   :height: 37
   :target: http://sourceforge.net


Pubsub Users
-------------

Several users have donated a bit of their time to describe how they use
pubsub in their Python projects.

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
    Shape models (rectangle, polygons etc) use pubsub to notify the GUI of
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
    Listomax (http://www.listomax.com/) uses version 1 of pubsub for MVC:
    multiple View (UI) components may need to change when the Model
    changes; simpler than direct calls, lower coupling.


*Mike Driscoll, for PyTimesheet and Zimbra Alerts, since 2007*:
    I use wx.lib.pubsub in two internal projects at my employer's business,
    "PyTimesheet" and the "Zimbra Alerts". I use it to send information
    between various frames, such as an options menu back to the main
    application that launched it. The main application I use it for though
    is a Timesheet program where I use it to tell my program which frame to
    display when. Basically when one closes, I need another one to open and
    I found that pubsub made this quite trivial. The other program is used
    in conjunction with our Zimbra web mail and will pop-up an alert when we
    receive an email and it also has an Outlook-like Reminder dialog for
    appointments... And thanks for providing such a nice tool for my
    arsenal!


*Anthony Floyd, RAVEN, since 200?*:
    Our project is called "RAVEN", it's an analytical and finite-element
    analysis program for simulating and analyzing the processing of
    composite materials in the aerospace industry. We use pubsub as
    the communications backbone.  We essentially have a MVC
    framework, and use pubsub to have the UI respond to things happening in
    the data.  However, we also use it to have data objects respond to
    changes in other data objects.

    We're quite enamoured with pubsub! It's proven to be an effective way
    to keep the UI out of the backend, and an effective way to keep the
    backend modularized.


*Sebastian Zurek, OpenSynergy, since 2007*:
    I'm using wx.lib.pubsub module as part of the OpenSynergy framework
    (http://www.opensynergy.pl, temporarily offline) that I am developing,
    and I found it VERY usefull. Pubsub is used as the communication layer
    betteen the extensions components and the framework, between the Model
    and Visual, and between the Visual elements.


*Werner F. Bruhin, for the The Wine Cellar Book, since 2006*
    Have been using pubsub for years and since I started work on version 4 of 
    my application [http://thewinecellarbook.com)] over a year ago I switched to 
    the pubsub v3 API and defined a topic tree.  Having a topic tree is just 
    great as you make sure that you don't mistype the topic names and on top you 
    have nice documentation on what topics you already defined and what 
    parameter(s) need to be passed for each topic.

    Currently I have topics to keep track of database state, data 
    needs saving, database item/row has changed, was deleted etc which trigger 
    updates to relevant lists to update themselves if needed and to show 
    messages on a wx.InfoBar. 


*Mike Rooney, for wxBanker, since 2006*:
    I use pubsub as the crucial event handling mechanism for wxBanker
    (https://launchpad.net/wxbanker). It works well for implementing design
    patterns such as MVC where you want to eliminate coupling, since it
    doesn't require that you know specific method names or implementation
    details of other classes, modules, or libraries. Pubsub is also great
    when you want to make an announcement without requiring that anything
    (or how many things) is listening to or acting upon that announcement.
    In short, pubsub makes intra-process communication a dream come true.


*QVI (http://www.qvii.com/) for several applications, since 2006*:
    Here at QVI we use pubsub for most of our wxPython applications (notably
    SmartTree), to achieve very lightweight, simple, and readable
    communication between classes and modules. One of the nice aspects of
    pubsub is how easy it is to incorporate into existing code, and how
    well-suited it is for pluggable/modular designs which want to make
    announcements about events, but don't require that or care if any other
    module is listening. It makes handling "events" easy, whatever we define
    them to be, and removes the need for the handlers to have any specific
    knowledge of how the announcements are made or where they came from.

    After discovering we could use pubsub independently of wxPython, we also
    use it in an application or two that doesn't use wxPython at all, but
    where we still desire a lightweight event handling mechanism (when don't
    you?).


*Author, for several applications, since 2004*:
    I have used PyPubSub on several projects. Applications which, for example, 

    - show tree structures with selectable nodes, and selected node's
      associated information panel 
    - show objects on information panels with info regarding progress
      of other components (running on other machines) updated in 
      real time
    - show dialog boxes with with entry fields for settings
    - have several panels in a wizard style to configure a task for execution

    With PubSub, one event occurs due to a mouse click on an icon, and
    and all parts of the code that need updating get called with the new
    data. This means automatic update of menu items (adding, removing etc),
    state in various panels, etc. Gone are the long sequences of calls
    through the code.
    
    Last time I had to build or maintain a Python event-based
    application was 2009, but I'm dedicated to maintaining pypubsub for other 
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

Pubsub was originally created by Robb Shecter as a module in the
wxPython library, named wx.lib.pubsub. In spring of 2004, I added the
ability of the module to use weak references, even to methods, and I
asked Robin Dunn if he would like the changes to be put in
wx.lib.pubsub. Robb and Robin liked them so much that they offered that
I take over ownership of the pubsub package.

The package was stable and fairly well scoped such that only a few minor
tweaks and improvements happened after that. In 2006 when I used pubsub
on some larger projects, I wished that topic trees and the topic message
data could be documented, and that more data could be passed more
easily. I also wished I could find a strategy that would allow the use
of tools like pylint to point out invalid topic names.

So I developed version 2 of the library. In fall 2006 I created an entry
in the Python Cheeseshop as PyPubSub
(http://pypi.python.org/pypi/PyPubSub) and used the cheese shop to hold
snapshots of my files. This way, developers not using wxPython can 
benefit from the publish/subscribe mechanism that it provides.

In May 2007 I decided it was time to create a project on SF.net for it. 
It is http://sourceforge.net/projects/pubsub, so the web site is at 
http://pubsub.sourceforge.net. Note that there also exists 
http://sourceforge.net/projects/pypubsub and http://pypubsub.sourceforge.net 
which are completely unrelated to this project. The details might be 
interesting, if only for historical purposes: 

    I wanted my SF.net project ID to be pypubsub to match the entry on 
    CheeseShop, but turns out pypubsub was already used by another sourceforge project: one that did not have an entry on Cheese Shop -- 
    or any code on SF.net for that matter -- and was more recent that mine. 
    The author did accept to rename his SF.net project (renamed to *Python 
    Messaging Service* (PMS)), but the ID could not be changed.
    So I kept the name PyPubSub, but I had to settle for the less descriptive ID 'pubsub' on SF.net, leading to a project page
    at http://sourceforge.net/projects/pubsub/ and a website at 
    http://pubsub.sourceforge.net. 
    
    I was hoping the author would move his 
    project to a different SF.net ID, easy for him so no data (code, issue tickets, forums etc). The author said he would edit the snapshots on his 
    web sites that show an image with the word "PyPubSub". These images would be
    confusing to visitors that aren't familiar with the "real/original" 
    PyPubSub. 
    
After using version 2 for a bit I wasn't really happy with it so I started 
work version 3 before I got to beta of 2. Version 3.0.0, completed some time 
in 2008, added support for documenting
topics, a more OO topic tree, keyword data to be sent along with the topic 
message and topic argument specification to allow for more validations. Version
3 also supports a more versatile notification mechanism that allows messages to 
be sent when certain things happen in the pubsub module, e.g. a listener 
subscribes. 

However the version of PyPubSub in wxPython was still version 1 API, with
an option to use version 2 or 3 via some settings set at import time. Everytime 
I updated pubsub, the changes had to be copied into wxPython's ``wx.lib.pubsub``.
This was annoying, plus I realized that if I didn't depracate the v1 API the new 
one would stay unused for a while longer (inertia!). This led to version 3.1.0 
in early 2010, this supported v1 API in version 3, and supported migration from 
old to new. This was tough but worked well and meant that wx/lib/python could 
be a verbatim copy of PyPubSub/src/pubsub folder. 

Not much happened between that time and first half of 2013, except for a minor 
release 3.1.2 in November 2011: the code was stable and did its job nicely so no 
major changes needed. Also in that period I didn't develop or maintain any 
event-based Python application so I didn't have any reason to update PyPubSub. I 
did accumulate about a dozen tickets on SF.net involving bugs or patches 
contributed by users in that period. 

Prompted by the overhaul of wxPython 
'Phoenix' in 2013, I removed all the code that was there just to support the old 
version 1 API. I took the opportunity to address the dozen tickets during the 
summer of 2013, and redesign the docs. During that period I also found a user 
who had clone PyPubSub to github without mentioning intent, giving credit etc; 
but no code edits either so was probably to have as a backup for one of his 
projects that required a specific version of it, but still, there are already 
enough pubsub's on the net, no need to confuse developers even more. Also found
recent project with same name, much smaller scale, hopefully the author will change it and just join this project. And the sf.net/projects/pypubsub is still 
there but hasn't been maintained since 2008.  


