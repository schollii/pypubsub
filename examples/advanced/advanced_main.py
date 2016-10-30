"""
Advanced example that shows other capabilities of pubsub such as pubsub notification, listener
exception handling, and topic definition providers.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from pubsub import pub

import notifhandle
import exchandle

import kwargs_topics

# ***** actual application **********

print('Using "kwargs" messaging protocol of pubsub v3')

try:
    print('------- init ----------')

    pub.addTopicDefnProvider(kwargs_topics, pub.TOPIC_TREE_FROM_CLASS)
    pub.setTopicUnspecifiedFatal()

    import kwargs_listeners
    import kwargs_senders as senders

    print('-----------------------')
    senders.doSomething1()
    senders.doSomething2()

    print('------- done ----------')

    print('Exporting topic tree to', kwargs_topics.__name__)
    pub.exportTopicTreeSpec('kwargs_topics_out')

except Exception:
    import traceback

    traceback.print_exc()
    print(pub.exportTopicTreeSpec())

print('------ exiting --------')
