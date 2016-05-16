"""

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""

import console_listeners
import console_senders as senders


def run():
    print('Using "kwargs" messaging protocol of pubsub v3')

    senders.doSomething1()
    senders.doSomething2()


if __name__ == '__main__':
    run()
