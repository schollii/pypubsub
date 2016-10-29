"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

from pubsub import py2and3
from pubsub.utils import notification

def testNotifications():
    capture = py2and3.StringIO()
    logger = notification.useNotifyByWriteFile(capture)
    from pubsub import pub
    def block():
        def listener(): pass
        pub.subscribe(listener, 'testNotifications')
    block()

    
