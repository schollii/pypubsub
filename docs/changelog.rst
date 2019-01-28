Changelog
---------

High-level changelog. For details, consult the SVN logs.

:4.0.3 (Jan 2019):

* Cleanup for Python 3.7 (mostly add support for keyword-only args, use
    Python 3 inspect signature/Parameter and add tests for

:4.0.0 (Dec 2016):

* Verified support Python 3.5 and 3.6
* Distribution via wheel
* Abandon support for Python 2.x and easy_install; now requires Python >= 3.3
* Abandon support for long-ago deprecated arg1 messaging protocol
* Added currying of subscribed listener args
* Significant speed improvement for message delivery
* Use PEP 484 style of annotations throughout
* Use enum instead of constants when practical


:3.3.0 (Feb 2014):

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
  string, thereby enabling python editors to support PyPubSub-based development via
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
- PyPubSub can be installed inside other packages and will not interfere with
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
  PyPubSub such as "subscribe", "sendMessage".
- Support user-defined exception handling of exceptions raised by
  listeners
- Proto-Documentation on own website using Sphinx
- Separate regression testing folder for nose-based automated testing
- Configuration module for choosing which PyPubSub API to use in application,
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

