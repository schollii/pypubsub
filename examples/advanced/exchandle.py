"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

import traceback

from pubsub import pub


# create one special notification handler that ignores all except
# one type of notification
class MyPubsubExcHandler(pub.IListenerExcHandler):
    def __call__(self, listenerID: str, topicObj: pub.Topic):
        print('Exception raised in listener %s during sendMessage()' % listenerID)
        traceback.print_exc()


pub.setListenerExcHandler(MyPubsubExcHandler())
