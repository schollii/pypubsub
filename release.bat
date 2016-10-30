REM Run this script: it indicates specific steps to follow,
REM and generates the distributions.
REM
REM Oliver, Dec 2015

echo off

echo ==============================================================
echo Follow the instructions in Release section of Dev docs
echo BEFORE continuing; pressing ENTER will create distributions
echo for new version and UPLOAD them to PyPi:
pause

python setup.py sdist bdist_wheel
twine dist

echo ==============================================================
echo Upload completed.
echo Follow remaining instructions in Release section of Dev docs.
