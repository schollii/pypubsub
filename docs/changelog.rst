Changelog
----------

High-level changelog. 

:3.4.0 (Mar 2019):

PyPubSub 3.4 was created because I somehow did not include all source files (for 
testing and docs) in the source distribution of 3.3 when I moved it from SourceForge 
to github, and Python 2.7 has lived on longer than I expected when I created the 4.0 
release a couple of years ago (where I dropped support for Python 2.x). As mentioned 
root README.txt, PyPubSub is only for Python 2.7. Use PyPubSub 4+ for Python 3+.

* moved source code from SourceForge to github
* Abandon support for easy_install and arg1 protocol
* Added currying of subscribed listener args
* make specific to Python 2.7, ie removed code related to support both 2.7 and 3.x 
  (use PyPubSub 4+ for Python 3+)
* use pytest instead of nose

:3.3.0 (Nov 2013):

* cleanup low-level API: exception classes, moved some out of pub module that did not
  belong there (clutter), move couple modules; specifically:

  * Removed from pub (available on object returned from pub.getDefaultTopicMgr())
    * getOrCreateTopic -> pub.getDefaultTopicMgr().getOrCreateTopic
    * getTopic  -> pub.getDefaultTopicMgr().getTopic
    * newTopic  -> pub.getDefaultTopicMgr().newTopic
    * delTopic -> pub.getDefaultTopicMgr().delTopic
    * getAssociatedTopics -> pub.getDefaultTopicMgr().getTopics
    * getDefaultTopicTreeRoot -> pub.getDefaultTopicMgr().getRootAllTopics
  * Removed from pub (available from pubsub.core):
    * ITopicDefnProvider
  * Moved from pub into to pubsub.core.TopicDefnProvider class as classmethod:
    * registerTopicDefnProviderType
  * Renamed:
    * TopicNameInvalid -> TopicNameError
    * UndefinedTopic(RuntimeError) -> TopicNameError(ValueError)
    * UndefinedSubtopic(RuntimeError) -> TopicNameError(ValueError)
    * ListenerInadequate(TypeError) -> ListenerMismatchError(ValueError)
    * UnrecognizedImportFormat -> UnrecognizedSourceFormatError
    * ListenerSpecInvalid -> MessageDataSpecError
    * SenderMissingReqdArgs -> SenderMissingReqdMsgDataError
    * SenderUnknownOptArgs -> SenderUnknownMsgDataError
    * ListenerNotValidatable -> TopicDefnErrorcd
  * Changed;
    * Topic.isSendable -> hasMDS
    * TopicManager.??? -> isTopicInUse + hasTopicDefinition

* completed the ref docs
* support installation via pip
* cleanup versioning metadata: use pubsub.__version__ instead of pub.PUBSUB_VERSION
* support Python 3
* add getListenersIter() to iterate over listeners without temp copy of listener list
* add deprecation message when import setuparg1
* new wxPubsubMonitor utility class

:3.2.0 (sep 2013):

- cleanup of docs
- merged importTopicTree to addTopicDefnProvider
- renamed pub.getDefaultRootAllTopics to pub.getDefaultTopicTreeRoot
- removed pub.importTopicTree, use pub.addTopicDefnProvider(source, format)
- renamed pub.exportTopicTree to pub.exportTopicTreeSpec
- several minor bug fixes
- incorporated some patches contributed by users: one for performance improvement when
  high-frequency of subscribers/messages; one for reading topic tree specification from
  XML rather than .py module
- v1 and v2 APIs no longer supported

:3.1.2 (2011):

- added some docs
- more configurable importTopicTree
- using importTopicTree now allows to use the topic hierarchy as topic names instead of
  string, thereby enabling python editors to support pubsub-based development via
  code completion and sendMessage keyword arguments.

:3.1.1b (2010):

- cleanup docs
- couple minor tweaks (for instance added pub.getMsgProtocol())

:3.1.0b (2009):

- Import/export of topic tree and its documentation using Python interpreter
- Better support for evolving topic tree during application development,
  with "freezing" certain parts of tree
- Helper functions to transition from *arg1* to *kwargs* messaging protocol
- Improved error messages (in exceptions raised)
- pubsub can be installed inside other packages and will not interfere with
  system-wide pubsub
- pubsubconf module moved inside pubsub package so manual install easier
- Support !**kwargs in listeners
- Support for more than one pubusb notification handler
- Multiple publisher engines in one application (for instance, in separate
  threads, or for different "domains" in a large application)
- Upgraded docs
- Bug fixes, cleanup

:3.0 (2008):

- Use keyword arguments in sendMessage
- Support any kind of listener, not just those with one unnamed argument
- Validate listeners at subscription time
- Support "inheritance" of keyword arguments by subtopics during
  message sending (prevents a common bug which was to send data using
  wrong argument names).
- Topic tree can be documented (including topic message arguments)
- Support user-defined notification handling of certain events occuring in
  pubsub such as "subscribe", "sendMessage".
- Support user-defined exception handling of exceptions raised by
  listeners
- Proto-Documentation on own website using Sphinx
- Separate regression testing folder for nose-based automated testing
- Configuration module for choosing which pubsub API to use in application,
  useful for backwards compatibility

:2.0 (2007):

- more Pythonic API (new ``PublisherClass`` API, at module level
  so easier to call -- no need to know about singleton)
- Support definition of topic tree via a python class, for increased
  rigor and documentability of topics
- Topics are objects

:1.0 (2005):

- Given its own "home" as separate package from wxPython's ``wx.lib.pubsub``
- Factored out weakmethod
- Put on Cheese Shop

:Pre 1.0:

- Created by Rob Shecter in wxPython's ``wx.lib`` (early 2000?)
- Weakmethod added by Oliver Schoenborn (2004)
- Further development transfered to Schoenborn (2004)

