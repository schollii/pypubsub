'''
Timing helper function to time several Python statements. It makes 
using the timeit module much more convenient. The only important
function is times(), to which you provide the number of iterations
to time, an initialization statement (typically, to initialize some 
locals), and the list of statements to time. E.g. 

    times(init='l=range(1,1000)', 
            s1='if l!=[]: pass', 
            s2='if l: pass', 
            s3='if len(l): pass')

will print(out)

s2 => 0.046
s1 => 0.086
s3 => 0.121

showing that s2 is the fastest (in fact, two to three times faster
than the alternatives). 
'''

from timeit import Timer

class Timing:
    def __init__(self, name, num, init, statement):
        self.__timer = Timer(statement, init)
        self.__num   = num
        self.name    = name
        self.statement = statement
        self.__result  = None
        
    def timeit(self):
        self.__result = self.__timer.timeit(self.__num)
        
    def getResult(self):
        return self.__result
        
        
def times(num=1000000, reverse=False, init='', **statements):
    '''The num is the number of times that each statement will 
    be executed. The init statement is executed only once for 
    statement and is not part of the timing result. The 
    statements kwarg is a dict of statements to time, where key
    is a 'name' for the statement, and value is the statement
    (as a string). Prints the timings from smallest to largest
    (unless reverse=True, then opposite). '''
    # time each statement
    timings = []
    for n, s in statements.iteritems():
        t = Timing(n, num, init, s)
        t.timeit()
        timings.append(t)
    
    # print(results)
    timings.sort(key=Timing.getResult, reverse=reverse)
    for t in timings:
        print("  %10s => %.3f s" % (t.name, t.getResult()))
    
    
if __name__ == '__main__':
    inits = ('l=range(1,1000)', 'l=[]')
    for ii in inits:
        print('\nFor %s:' % ii)
        times(init=ii, 
            boolean = 'if l: pass', 
            empty   = 'if l!=[]: pass', 
            len_    = 'if len(l): pass')
        
    print('\nFor list -> dict:')
    times(100, init='l=range(1,1000)', 
        zip      = 'dict(zip(l[::2], l[1::2]))', 
        listcomp = 'dict((l[i],l[i+1]) for i in range(0,len(l)-1,2))')
        
    print('\nFor hasattr vs except:')
    times(10000, init='class Foo: pass\nfoo = Foo()', 
        hasattr = 'if hasattr(foo, "a"): a = getattr(foo, "a")',
        excep   = 'try: a = foo.a\nexcept Exception: pass')
    
    print('\nFor cost of enumerate:')
    times(100, init='l=range(1,1000)\ndef f(v): return (v*10-50)/2', 
        enum = 'for i, v in enumerate(l): f(v)',
        noenum = 'for v in l: f(v)',
        count = 'ii=0\nfor v in l: \n  f(v)\nii += 1')
        
    print('\nFor slice before/in loop:')
    times(100, init='l=range(0,10000)\nl2=range(0,1000)', 
        before10k = 'l3=l[9000:]\nfor i in l3: pass',
        before1k  = 'l3=l2[1:]\nfor i in l3: pass',
        inloop10k = 'for i in l[9000:]: pass',
        inloop1k  = 'for i in l2[1:]: pass',
        range     = 'for i in xrange(9000,10000): l[i]',
        nocopy    = 'for i in l2: pass')