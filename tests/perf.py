"""
Measure performance of pubsub, so that impact of proposed performance enhancing
algorithms can be proven. Measure with 

    python -m timeit -n1 "import perf; perf.runTest(proto)"
    
with proto='kwargs' or 'arg1'.

Results as of 3.2.0: 7.5 s for kwargs protocol, 5.6 for arg1 protocol. 

NOTE: The tests are useful to capture a regression in speed of each pubsub 
protocol, they are not useful to compare the speed of both protocols. This 
is because the test uses listeners that do NO processing whatsoever, 
whereas in most applications, the handling of messages within listeners 
will be more compute intensive than the dispatching of the messages via 
either protocol. Although kwargs appears somewhat slower than arg1, a 
typical application will see no gain by using arg1 over kwargs, and will be 
less maintainable. Also, for kwargs the message data is directly usable 
within a listener, whereas for arg1 a field access is required for every 
data, which in a typical arg1-based application will increase message 
handling time. 

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.

"""


from pubsub import py2and3


def prepTest(protoVersion):
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
    
    class Foo: pass
    class Bar: pass
    class Baz: pass
    class Fim: pass

    # different types of arguments that will be passed to listeners
    argVals = dict(
       nn = (1, 2, 3, 4, None),
       ss = ('a', 'b', 'c', 'd', None),
       ff = (sin, cos, asin, acos, None),
       mm = (sys, os, glob, platform, None),
       cc = (Foo, Bar, Baz, Fim, None),
       )
    
    # ---------------- Adapter classes: addapt listeners and senders ----------

    class TestPerfArg1:

        def __init__(self):
            self.called = [False]*6

        def listener1(self, msg=None): self.called[1] = True
        def listener2(self, msg): self.called[2] = True
        def listener3(self, msg): self.called[3] = True
        def listener4(self, msg): self.called[4] = True
        def listener5(self, msg): self.called[5] = True
    
        def sendMsg(self, topic, args):
            pub.sendMessage(topic, args)
        
        def getArgNames(self, listeners):
            'No intro available for getting args, just return from expectArgNames'
            return dict( (topic, expectArgNames[topic]) for topic in listeners.keys() )
        
    class TestPerfKwargs:

        def __init__(self):
            self.called = [False]*6

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
            names = dict( (topic, argKeys(topic)) for topic in listeners.keys() )
            assert [set(expectArgNames[topic]) == set(argKeys(topic)) for topic in listeners.keys()] == [True]*5
            return names


    # ------------------------------------
    
    if protoVersion == 'arg1':
        from pubsub import setuparg1
        from pubsub import pub
        tester = TestPerfArg1()
        
    else:
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
    
    assert tester.called == [False]*6

    def randVal(k):
        vals = argVals[k]
        return vals[ randint(0, len(vals)) ]

    numTopics = len(topics)
    def setupTopicAndArgs():
        topic = topics[ randint(0, numTopics) ]
        args = dict( (argName, randVal(argName)) for argName in topicArgNames[topic] )
        return topic, args

    #assert tester.called == [False]+[True]*5
    # print 'Test run %s completed' % testNum

    return setupTopicAndArgs, tester


def printDescription(numTests):
    import sys
    py2and3.print_("Python version %s" % sys.version)
    py2and3.print_("Randomized topic send message: %s tests" % numTests)


def runPerfTest():
    # ---------------- init from command line ----------
    import sys
    if len(sys.argv) > 1:
        numTests = int(sys.argv[1])
        proto = sys.argv[2]
        if proto == 'description':
            printDescription(numTests)
            sys.exit()
    else: # default run without command line args
        numTests = 10**5
        proto = 'kwargs'
        printDescription(numTests)

    # ----------- time pubsub send message -------------
    from timeit import timeit
    setupStr = 'from __main__ import prepTest; setupTopicAndArgs, tester = prepTest("%s")' % proto
    totalTime = timeit('t, a = setupTopicAndArgs(); tester.sendMsg(t, a)',
                        setup = setupStr, number = numTests)

    result = 'Time for %s protocol: %7.4s' % (proto, totalTime)
    py2and3.print_(result)


def runProfileTest():
    import sys
    if sys.argv[2] != 'kwargs':
        return

    py2and3.print_("Python version %s" % sys.version)

    import cProfile as profile
    import pstats

    global setupTopicAndArgs, tester
    setupTopicAndArgs, tester = prepTest("kwargs")

    fname = 'perf.prof'
    if len(sys.argv) > 1:
        numRuns = int(sys.argv[1])
    else:
        numRuns = 10000
    statement = 'for ii in range(0,%s): t, a = setupTopicAndArgs(); tester.sendMsg(t, a)' % numRuns
    profile.run(statement, filename=fname)

    stats = pstats.Stats(fname)
    stats.strip_dirs()
    #stats.sort_stats('time')
    #stats.print_stats(20)
    stats.sort_stats('filename', 'line')
    #stats.print_stats()
    stats.print_callers()
    #stats.sort_stats('cumulative')
    #stats.print_stats(20)


if __name__ == '__main__':
    runPerfTest()
    #runProfileTest()
