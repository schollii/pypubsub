"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

from pubsub import pub


def doSomething1():
    print('--- SENDING topic1.subtopic11 message ---')
    pub.sendMessage('topic1.subtopic11', msg='message for 11', extra=123)
    print('---- SENT topic1.subtopic11 message ----')


def doSomething2():
    print('--- SENDING topic1 message ---')
    pub.sendMessage('topic1', msg='message for 1')
    print('---- SENT topic1 message ----')
