
from setuptools import setup, find_packages


def getPackagesToDistribute():
    packages = find_packages('src')
    import sys
    setupCmd = sys.argv[1]
    if setupCmd in ['sdist', 'bdist', 'bdist_egg', 'bdist_wininst']:
        print( '*'*40 )
        print( 'Packaging:', packages)
        print( '*'*40)
    return packages


def getPubsubVersion():
    import sys
    sys.path.insert(0, 'src')
    import pubsub
    return pubsub.__version__


def getInstallRequires():
    import sys
    if sys.version_info < (3,5):
        return ['typing']
    return []


setup(
    name         = 'Pypubsub',
    version      = getPubsubVersion(),
    description  = 'Python Publish-Subscribe Package',
    keywords     = "publish subscribe observer pattern signal signals event events message messages messaging dispatch dispatching",
    author       = 'Oliver Schoenborn (aka "schollii")',
    author_email = 'oliver.schoenborn@gmail.com',
    url          = 'https://github.com/schollii/pypubsub',
    license      = "BSD License",
    zip_safe     = False,

    packages     = getPackagesToDistribute(),
    package_dir  = {'': 'src'},
    package_data = {'pubsub': ['LICENSE_BSD_Simple.txt', 'RELEASE_NOTES.txt']},
    install_requires=getInstallRequires(),

    classifiers  = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # use the module docs as the long description:
    long_description = open('README.rst', 'r').read()
)


