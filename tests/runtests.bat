echo off

rem    NOTE: All command line parameters will be passed on to nosetests
rem
rem    This script runs nosetests on all test subfolders;
rem    nose-cov (https://pypi.python.org/pypi/nose-cov) is used to generate
rem    coverage metrics.
rem
rem    Oliver Schoenborn

echo.
echo.
rem --verbose to get test names
rem --pdb to drop into debugger on error
set exepath=python -m nose.core
rem set exepath=c:\pypy-2.1\pypy -m nose.core --verbose --pdb
echo Using %exepath% for Python interpreter
shift


echo.
echo.
echo 1. ######################## PUBSUB config #########################
echo.

pushd config_no_auto
%exepath% --with-isolation
popd

echo.
echo.
echo 2. ######################## PUBSUB kwargs #########################
echo.

pushd pubsub_kwargs
%exepath% --with-cov --with-isolation

popd


echo.
echo.
echo 3. ######################## PUBSUB arg1 #########################
echo.

pushd pubsub_arg1
%exepath%  --with-cov
rem %exepath%\coverage -b -i -d cover_html
popd

echo.
echo.
echo 4. ##################### PUBSUB trans arg1 to kwargs messaging #######################
echo.

pushd trans_arg1_to_kwargs
%exepath% --with-isolation
popd



