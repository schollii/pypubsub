"""
Measure performance of pubsub, so that impact of proposed performance enhancing
algorithms can be proven. Measure with 

    python \python24\lib\timeit.py -n1 "import perf; perf.pubsubVer=N; perf.runTest()"
    
with N=version of pubsub (1 for version 1, 3 for version 3).

Results as of 3.0a8: 6.4 s (pubsub version 3)

Caution about comparing between version 1 and 3: this test uses 0 processing in the 
listeners, whereas in most applications, the handling of messages within listeners 
will be more compute intensive than the dispatching of the messages via either 
version of pubsub. So the conclusion from the results, i.e. that "version 3 is 
xx times slower than version 1", is unlikely to be correct: the numbers don't 
reflect the impact of pubsub on performance of your application, just the individual 
"raw" pubsub performance, so they can only be used to improve pubsub. 

In fact, it is very likely that you won't notice any performance difference between using 
either versions of pubsub (but you don't know an API's bottlenecks until you measure
hence this test), except when your listeners do almost nothing.

:copyright: Copyright since 2006 by Oliver Schoenborn, all rights reserved.
:license: BSD, see LICENSE.txt for details.
"""

testNum = 0
pubsubVer = 3

    
def runTest():
    # ---------------- init from command line ----------
    
    numRuns = 10**5
    global testNum
    testNum += 1
    if testNum == 1:
        py2and3.print_('Will test for pubsub version', pubsubVer)
    
    # --------- create arrays for random sampling -------
            
    from math import sin, cos, asin, acos
    import sys, os, glob, platform
    
    class Foo: pass
    class Bar: pass
    class Baz: pass
    class Fim: pass
    
    argVals = dict(
       nn = (1, 2, 3, 4, None),
       ss = ('a', 'b', 'c', 'd', None),
       ff = (sin, cos, asin, acos, None),
       mm = (sys, os, glob, platform, None),
       cc = (Foo, Bar, Baz, Fim, None),
       )
    
    # ---------------- Adapter classes: addapt listeners and senders ----------

    class Pubsub3Test:
        def __init__(self):
            self.called = [False]*6
            
        def listener1(self, ss, nn, ff): self.called[1] = True
        def listener2(self, ss, nn, ff): self.called[2] = True
        def listener3(self, ss, nn, ff): self.called[3] = True
        def listener4(self, ss, nn, ff): self.called[4] = True
        def listener5(self, ss, nn, ff): self.called[5] = True
        
        def sendMsg(self, topic, args):
            pub.sendMessage(topic, **args)
            
    class Pubsub1Test:
        def __init__(self):
            self.called = [False]*6
            
        def listener1(self, msg): self.called[1] = True
        def listener2(self, msg): self.called[2] = True
        def listener3(self, msg): self.called[3] = True
        def listener4(self, msg): self.called[4] = True
        def listener5(self, msg): self.called[5] = True
    
        def sendMsg(self, topic, args):
            pub.sendMessage(topic, args)
        
    # ------------------------------------
    
    if pubsubVer == 1:
        from pubsub import setupv1
        from pubsub import pub
        tester = Pubsub1Test()
        
    else:
        from pubsub import pub
        tester = Pubsub3Test()
        
    listeners = {
       't1': tester.listener1, 
       't1.s2': tester.listener2, 
       't1.st2.st3': tester.listener3, 
       't1.st2.st4': tester.listener4, 
       't1.st2.st3.st5': tester.listener5, 
       }
    
    for (topic, ll) in listeners.items():
        pub.subscribe(ll, topic)
        
    topicArgNames = ('ss', 'nn', 'ff')
    topics = list(listeners.keys())
    
    
    # ---------------RUN the test! ------
    
    assert tester.called == [False]*6
    
    from random import randrange as randint
     
    def randVal(k):
        vals = argVals[k]
        return vals[ randint(0, len(vals)) ]
    
    for run in range(0, numRuns):
        #if run % 1000 == 0: print '.',
        topic = topics[ randint(0, len(topics)) ]
        args = dict( (argName, randVal(argName)) for argName in topicArgNames )
        tester.sendMsg(topic, args)
        
    assert tester.called == [False]+[True]*5
    print('Test run %s completed' % testNum)
    

if __name__ == '__main__':
    runTest()
    