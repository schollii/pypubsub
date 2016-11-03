"""
Measure performance of pubsub, so that impact of proposed performance enhancing
algorithms can be proven. Measure with

    python -m timeit -n1 "import perf; perf.runTest()"

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from pathlib import Path
from time import perf_counter
from typing import Tuple

from pubsub import pub
from pubsub.core import Listener


topicMgr = pub.getDefaultTopicMgr()


def loop_subscribe(topic_names, listeners):
    topicMgr = pub.getDefaultTopicMgr()
    topicMgr.clearTree()

    num_samples = 1000
    start = perf_counter()
    for count in range(num_samples):
        for listener in listeners:
            for topic_name in topic_names:
                pub.subscribe(listener, topic_name)

    tot_time = (perf_counter() - start)

    return round(tot_time, 2)


def perf_subscribe():
    """
    Subscription involves inspecting listener to (upon first subscription to a topic) create the
    topic and its MDS or (upon subsequent subscriptions to same topic) verify its signature is
    compatible with topic MDS, then adding listener to topic listeners, and adding topic to
    topics mapping (of name to topic object). This suggests that complexity of signature and
    complexity of topic name are the two axes of performance for subscriptions, as the
    creation of a topic is not likely to be nearly as common as subscriptions to existing topics.

    Results indicate that deeper topics and listeners have only marginal (ie insignificant)
    overhead over shallow topics and listeners:
    - root topic and no-args listeners: 6.77
    - deep topics and no-args listeners: 6.83
    - root topics and many-args listeners: 6.8
    - deep topics and many-args listeners: 6.83
    """
    print("-"*40)
    print("Performance measurement for subscribing:")

    num_topics = 100
    num_listeners = 10

    # root topic and no-args listeners:
    topic_names = ['some_topic_' + str(topic_index) for topic_index in range(num_topics)]
    listeners = [lambda: n for n in range(num_listeners)]
    print('root topic and no-args listeners:', loop_subscribe(topic_names, listeners))

    # deep topics and no-args listeners:
    topic_names = ['rt.st.sst.ssst.leaf_topic_' + str(topic_index) for topic_index in range(num_topics)]
    print('deep topics and no-args listeners:', loop_subscribe(topic_names, listeners))

    # root topics and many-args listeners:
    topic_names = ['some_topic_' + str(topic_index) for topic_index in range(num_topics)]
    listeners = [lambda x, y, z, a, b, c: n for n in range(num_listeners)]
    print('root topics and many-args listeners:', loop_subscribe(topic_names, listeners))

    # deep topics and many-args listeners:
    topic_names = ['rt.st.sst.ssst.leaf_topic_' + str(topic_index) for topic_index in range(num_topics)]
    print('deep topics and many-args listeners:', loop_subscribe(topic_names, listeners))


def loop_send(subscriptions: Tuple[Listener, str], messages):
    topicMgr = pub.getDefaultTopicMgr()
    topicMgr.clearTree()

    for listener, topic_name in subscriptions:
        pub.subscribe(listener, topic_name)

    num_samples = 1000
    start = perf_counter()
    for count in range(num_samples):
        for topic_name, kwargs in messages:
            pub.sendMessage(topic_name, **kwargs)

    tot_time = (perf_counter() - start)

    return round(tot_time, 2)


def perf_send():
    """
    Sending message involves calling each listener with data, and going up the tree to root actor
    each level has fewer data so data must be filtered out.

    ----------------------------------------
    Performance measurement for sending:
    listeners ['obs1', 'obs2', 'obs3', 'obs4', 'obs5', 'obs6', 'obs7', 'obs8']
    topic names ['t1', 't1.t2', ..., 't1.t2.t3.t4.t5.t6.t7.t8']
    with depth 8:           with depth 8:         % less   X faster
        8 data 9.31             8 data 4.76         49      2.0
        4 data 8.48             4 data 4.48         47      1.9
        2 data 8.23             2 data 4.5          45      1.8
        1 data 8.26             1 data 4.31         48      1.9
        no data 8.05            no data 4.27        47      1.8
    with depth 4:           with depth 4:
        4 data 4.4              4 data 2.63         40      1.7
        2 data 3.96             2 data 2.56         35      1.5
        1 data 3.99             1 data 2.51         37      1.6
        no data 4.1             no data 2.43        40      1.7
    with depth 2:           with depth 2:
        2 data 2.28             2 data 1.61         29      1.4
        1 data 1.84             1 data 1.57         15      1.2
        no data 2.18            no data 1.52        30      1.4

    with depth 1:           with depth 1:
        1 data 1.2              1 data 1.1          8       1.1
        no data 1.24            no data 1.05        15      1.2
    """
    print("-"*40)
    print("Performance measurement for sending:")

    # root topic and no-args listeners:
    def obs1(arg1=None): pass
    def obs2(arg1=None, arg2=None): pass
    def obs3(arg1=None, arg2=None, arg3=None): pass
    def obs4(arg1=None, arg2=None, arg3=None, arg4=None): pass
    def obs5(arg1=None, arg2=None, arg3=None, arg4=None, arg5=None): pass
    def obs6(arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None): pass
    def obs7(arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None): pass
    def obs8(arg1=None, arg2=None, arg3=None, arg4=None, arg5=None, arg6=None, arg7=None, arg8=None): pass

    local_objs = locals().copy()
    listeners = [local_objs['obs' + str(n)] for n in range(1, 9)]
    print('listeners', [cb.__name__ for cb in listeners])

    topic_names = ['t1']
    for index in range(2, 9):
        topic_names.append(topic_names[-1] + ".t" + str(index))
    print('topic names', topic_names)

    num_messages = 100

    def sub_test(topic_names):
        subscriptions = [(obs, name) for obs, name in zip(listeners, topic_names)]
        num_topics = len(topic_names)
        num_subs = len(subscriptions)

        print('with depth {}:'.format(num_topics))

        if len(topic_names) >= 8:
            msg_data = dict(arg1=1, arg2=2, arg3=3, arg4=4, arg5=5, arg6=6, arg7=7, arg8=8)
            messages = [(topic_names[-1], msg_data)] * num_messages
            print('    {} data'.format(len(msg_data)), loop_send(subscriptions, messages))

        if len(topic_names) >= 4:
            msg_data = dict(arg1=1, arg2=2, arg3=3, arg4=4)
            messages = [(topic_names[-1], msg_data)] * num_messages
            print('    {} data'.format(len(msg_data)), loop_send(subscriptions, messages))

        if len(topic_names) >= 2:
            msg_data = dict(arg1=1, arg2=2)
            messages = [(topic_names[-1], msg_data)] * num_messages
            print('    {} data'.format(len(msg_data)), loop_send(subscriptions, messages))

        if len(topic_names) >= 1:
            msg_data = dict(arg1=1)
            messages = [(topic_names[-1], msg_data)] * num_messages
            print('    {} data'.format(len(msg_data)), loop_send(subscriptions, messages))

        messages = [(topic_names[-1], {})] * num_messages
        print('    {} data'.format('no'), loop_send(subscriptions, messages))

    sub_test(topic_names)
    sub_test(topic_names[:4])
    sub_test(topic_names[:2])
    sub_test(topic_names[:1])


if __name__ == '__main__':
    perf_subscribe()
    perf_send()