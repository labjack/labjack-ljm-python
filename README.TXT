LJMPython
07/01/2013
support@labjack.com


The Python wrapper package, modules and examples for the cross-platform LJM
library.


Installation Requirements:

* Windows, Mac OS X, or Linux
* LJM library: http://labjack.com/support/ljm
* Python 2.5, 2.6 or 2.7. Python 3.x is currently not supported.
  
  Note to Python 3.x users: The Python program 2to3 can be used on the examples
  and wrapper source code in the labjack directory to translate the Python 2
  code to Python 3.


Installation:

After fulfilling the requirements, open a terminal/console and go to the
LJMPython root directory. To install LJMPython run the following command (Leave
off the sudo on Windows):

    $ sudo python setup.py install


Examples:

Example code can be found in the Examples directory.


Documentation:

LJM Python documentation can be found in the docstrings of the source code. The
source code files are located in the labjack/ljm directory.

Alternatively, after installation in Python you can use the help function on a
package/module for documentation. For example:

    import labjack.ljm
    help(labjack.ljm)

LJM library documentation can be found in the LJM User's Guide:

    http://labjack.com/support/ljm/users-guide


License:

All LJMPython packages, modules and examples are licensed under MIT X11. The
license can be found in the LICENSE.TXT file.
