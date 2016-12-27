echo off

REM Run this script: it indicates specific steps to follow,
REM and generates the distributions.
REM
REM Oliver, Dec 2016

echo ==============================================================
echo Before continuing, consult the instructions in Release
echo section of Dev docs.
echo ==============================================================
echo Creating source distribution:
python setup.py sdist

echo ==============================================================
echo Creating wheel distribution:
python setup.py bdist_wheel

echo ==============================================================
echo To UPLOAD the dist/* distributions to PyPi, press ENTER,
echo OTHERWISE, press ctrl-c:
pause

twine upload dist/*

echo ==============================================================
echo Upload completed.
echo Follow remaining instructions in Release section of Dev docs.
