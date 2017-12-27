@ECHO OFF

ECHO Installing LJM Python for all Python installs on David's computer.
ECHO LJM Python supports 32 and 64-bit Python 2.6, 2.7, and 3.x.
ECHO.

cd ..
python26_32 setup.py install || goto :done
ECHO.
python26_64 setup.py install || goto :done
ECHO.
python27_32 setup.py install || goto :done
ECHO.
python27_64 setup.py install || goto :done
ECHO.
python35_32 setup.py install || goto :done
ECHO.
python35_64 setup.py install || goto :done
ECHO.
python36_32 setup.py install || goto :done
ECHO.
python36_64 setup.py install || goto :done
ECHO.

ECHO Success!

:done
pause
