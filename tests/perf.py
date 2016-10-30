"""
Measure performance of pubsub, so that impact of proposed performance enhancing
algorithms can be proven. Measure with

    python -m timeit -n1 "import perf; perf.runTest()"

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

from pathlib import Path


def prepTest():
    from random import randrange as randint

    # --------- create arrays for random sampling -------

    # ss strings
    # nn numbers
    # ff functions
    # mm modules
    # cc classes
    expectArgNames = {
        't1': ('ss',),
        't1.s2': ('ss', 'nn'),
        't1.st2.st3': ('ss', 'nn', 'ff'),
        't1.st2.st4': ('ss', 'nn', 'ff', 'mm'),
        't1.st2.st3.st5': ('ss', 'nn', 'ff', 'mm', 'cc'),
    }

    from math import sin, cos, asin, acos
    import sys, os, glob, platform

    class Foo:
        pass

    class Bar:
        pass

    class Baz:
        pass

    class Fim:
        pass

    # different types of arguments that will be passed to listeners
    argVals = dict(
        nn=(1, 2, 3, 4, None),
        ss=('a', 'b', 'c', 'd', None),
        ff=(sin, cos, asin, acos, None),
        mm=(sys, os, glob, platform, None),
        cc=(Foo, Bar, Baz, Fim, None),
    )

    # ---------------- Adapter classes: addapt listeners and senders ----------

    class TestPerfKwargs:

        def __init__(self):
            self.called = [False] * 6

        def listener1(self, ss): self.called[1] = True

        def listener2(self, ss, nn): self.called[2] = True

        def listener3(self, ss, nn, ff): self.called[3] = True

        def listener4(self, ss, nn, ff, mm): self.called[4] = True

        def listener5(self, ss, nn, ff, mm, cc): self.called[5] = True

        def sendMsg(self, topic, args):
            pub.sendMessage(topic, **args)

        def getArgNames(self, listeners):
            'Get arg names for topic, from list of listeners. Should be same as expectArgNames'
            topicMgr = pub.getDefaultTopicMgr()

            def argKeys(topic):
                topicObj = topicMgr.getTopic(topic)
                reqd, opt = topicObj.getArgs()
                assert topicObj.hasMDS()
                return reqd + opt

            names = dict((topic, argKeys(topic)) for topic in listeners.keys())
            assert [set(expectArgNames[topic]) == set(argKeys(topic)) for topic in listeners.keys()] == [True] * 5
            return names

    # ------------------------------------

    from pubsub import pub
    tester = TestPerfKwargs()

    listeners = {
        't1': tester.listener1,
        't1.s2': tester.listener2,
        't1.st2.st3': tester.listener3,
        't1.st2.st4': tester.listener4,
        't1.st2.st3.st5': tester.listener5,
    }

    for (topic, ll) in listeners.items():
        pub.subscribe(ll, topic)

    topicArgNames = tester.getArgNames(listeners)
    topics = list(listeners.keys())

    assert tester.called == [False] * 6

    def randVal(k):
        vals = argVals[k]
        return vals[randint(0, len(vals))]

    numTopics = len(topics)

    def setupTopicAndArgs():
        topic = topics[randint(0, numTopics)]
        args = dict((argName, randVal(argName)) for argName in topicArgNames[topic])
        return topic, args

    # assert tester.called == [False]+[True]*5
    # print 'Test run %s completed' % testNum

    return setupTopicAndArgs, tester


def printDescription(numTests):
    import sys
    print("Python version %s" % sys.version)
    print("Randomized topic send message: %s tests" % numTests)


def runPerfTest():
    # ---------------- init from command line ----------
    import sys
    if len(sys.argv) > 1:
        numTests = int(sys.argv[1])
    else:  # default run without command line args
        numTests = 10 ** 5

    printDescription(numTests)

    # ----------- time pubsub send message -------------
    from timeit import timeit
    setupStr = 'from __main__ import prepTest; setupTopicAndArgs, tester = prepTest()'
    totalTime = timeit('t, a = setupTopicAndArgs(); tester.sendMsg(t, a)',
                       setup=setupStr, number=numTests)

    result = 'Time (sec): %7.4s' % totalTime
    print(result)


def runProfileTest():
    import sys
    print("Python version %s" % sys.version)

    import cProfile as profile
    import pstats

    global setupTopicAndArgs, tester
    setupTopicAndArgs, tester = prepTest()

    for idx in range(10):
        fname = 'perf{}.pstats'.format(idx)
        if not Path(fname).exists():
            break

    if len(sys.argv) > 1:
        numRuns = int(sys.argv[1])
    else:
        numRuns = 10000
    statement = 'for ii in range(0,%s): t, a = setupTopicAndArgs(); tester.sendMsg(t, a)' % numRuns
    profile.run(statement, filename=fname)
    print("Profiling saved in", fname)

    stats = pstats.Stats(fname)
    stats.strip_dirs()
    # stats.sort_stats('time')
    # stats.print_stats(20)
    stats.sort_stats('filename', 'line')
    # stats.print_stats()
    stats.print_callers()
    # stats.sort_stats('cumulative')
    # stats.print_stats(20)


if __name__ == '__main__':
    runPerfTest()
    # runProfileTest()
