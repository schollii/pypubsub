# compatibility with both Python 2.x and 3.x:
import sys
def print_(*args):
    w = sys.stdout.write
    w( ', '.join(str(a) for a in args) )
    w( '\n' )
    
try:
    import setuptools
except:
    # setuptools not installed, so install it:
    print_('No setuptools found, trying to download')
    import ez_setup
    ez_setup.use_setuptools()
finally:
    from setuptools import setup, find_packages

    
def getPackagesToDistribute():
    packages = find_packages('src')
    import sys
    setupCmd = sys.argv[1]
    if setupCmd in ['sdist', 'bdist', 'bdist_egg', 'bdist_wininst']:
        print_( '*'*40 )
        print_( 'Packaging:', packages)
        print_( '*'*40)
    return packages

    
def getPubsubVersion():
    import sys
    sys.path.insert(0, 'src')
    import pubsub
    return pubsub.__version__
    
setup(
    name         = 'PyPubSub',
    version      = getPubsubVersion(),
    description  = 'Python Publish-Subscribe Package',
    author       = 'Oliver Schoenborn',
    author_email = 'oliver.schoenborn@gmail.com',
    url          = 'http://pubsub.sourceforge.net',
    download_url = 'http://downloads.sourceforge.net/pubsub',
    license      = "BSD",
    zip_safe     = False,
    
    packages     = getPackagesToDistribute(),
    package_dir  = {'': 'src'},
    package_data = {'pubsub': ['LICENSE_BSD_Simple.txt', 'RELEASE_NOTES.txt']},

    keywords     = "publish subscribe observer pattern signal signals event events message messages messaging dispatch dispatching",
    
    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Python Software Foundation License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
    # use the module docs as the long description: 
    long_description = open('README.txt', 'r').read()
)


