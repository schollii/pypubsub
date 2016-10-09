REM Run this script: it indicates specific steps to follow,
REM and generates the distributions.
REM
REM Oliver, Dec 2015

echo off

echo ==============================================================
echo Do these manually:
echo - In docs folder, regenerate HTML docs, confirm ok (make clean, make html)
echo - In root folder, run tox, confirm that all tests pass
echo - In examples folder, run each example and verify no exceptions
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
echo Will create distributions for new version:
pause

python setup.py sdist bdist_wheel

echo.
echo ==============================================================
echo Now do these manually:
echo - Update project website with docs
echo - Create new SVN tag for release
echo.

echo.
echo ==============================================================
echo Will register new version on Pypi:
pause

twine dist

echo - Verify new release on pypi.python.org
echo.

echo ==============================================================
echo Release DONE!
