LJMPython: Python wrapper module for the LJM library
01/25/2013
support@labjack.com

This package contains the LJMPython wrapper module and examples for the LJM
library. The LJM driver is a cross-platform Modbus driver for LabJack devices.

Requirements:

* Windows, Mac OS X, Linux
* LJM driver
* Python 2.5 or above. Python 3.x currently not supported.

Installation:

To install LJMPython, in a terminal/console go to this package's root directory
and run the following command (Leave off the sudo on Windows):

    $ sudo python setup.py install

Examples:

    The examples can be found in the Examples directory of this package.

Documentation:

    Refer to the docstrings in the source code for documention. The source code
    is located in the labjack/ljm directory's files of this package.

    Alternatively, after installation in a Python program you can use the help
    function on the module. For example:

        import labjack.ljm
        help(labjack.ljm)

    LJM library (dll/so/dylib) documentation can be found in the LJM User's
    Guide:
    
        http://labjack.com/support/ljm/users-guide

License:

All LJMPython modules and examples are licensed under MIT X11. The license can
be found in the LICENSE file.
