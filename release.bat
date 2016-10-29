REM Run this script: it indicates specific steps to follow, 
REM and generates the distributions. 
REM
REM Oliver, May 2010

echo off

echo ==============================================================
echo Do these manually: 
echo - In docs folder, regenerate HTML docs, confirm ok (make clean, make html)
echo - In root folder, run tox, confirm that all tests 
echo - In examples folder, run all and verify no exceptions
echo - Update src/pubsub/__init__.py for new version # (setup.py uses it)
echo - Update src/pubsub/RELEASE_NOTES.txt
echo - Update docs/changelog.txt: more details than release notes
echo - Update docs/index.rst and docs/installation.rst
echo - Regenerate docs, confirm ok
echo - Confirm that all tests in tests and examples folder run
echo - Commit to SVN
echo.

echo.
echo ==============================================================
echo Will creating distributions for new version:
pause

python setup.py sdist bdist_wininst bdist_egg

echo.
echo ==============================================================
echo Now do these manually: 
echo - Got to https://sourceforge.net/project/admin/explorer.php?group_id=197063
echo - Create a new folder for this release
echo - Upload all new files from dist folder to release folder on www.sf.net
echo - Select the latest zip file and set it as default for ALL
echo - Select the .exe file and set it as default for Windows
echo - Copy release notes to readme.txt and upload as regular file
echo - Use FileZilla to update docs on website
echo.

echo.
echo ==============================================================
echo Will registering new version on Pypi:
pause

python setup.py register

echo - Verify new release on pypi.python.org
echo - Add a URL for the release: must use "direct link" version, and get MD5 hash from SF.net
echo - Create new SVN tag for release
echo.

echo ==============================================================
echo Release DONE!
