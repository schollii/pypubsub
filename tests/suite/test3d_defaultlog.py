"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import io
from pubsub.utils import notification

def testNotifications():
    capture = io.StringIO()
    logger = notification.useNotifyByWriteFile(capture)
    from pubsub import pub
    def block():
        def listener(): pass
        pub.subscribe(listener, 'testNotifications')
    block()


