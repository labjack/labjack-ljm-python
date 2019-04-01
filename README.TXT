labjack-ljm : LJM library Python wrapper for LabJack T7 and T4
04/xx/2019
support@labjack.com


The Python wrapper package, modules and examples for the cross-platform LJM
library, which supports the LabJack T7 and T4.


Installation Requirements:

* Windows, Mac OS X, or Linux
* LJM library: https://labjack.com/support/software/installers/ljm
* Python 2.6, 2.7 and 3.x.


Installation:

After fulfilling the requirements, open a terminal/console and use pip to
install labjack-ljm for the first time:

pip install labjack-ljm

For upgrading to a newer version, use:

pip install labjack-ljm --upgrade

You can also run pip from your Python installation like so:

python -m pip install labjack-ljm

Alternatively, download the labjack-ljm distribution source, unzip the contents
and go to its unzipped directory. To install, run the the following command
(Leave off the sudo on Windows):

    $ sudo python setup.py install


Distribution Name Change:

The previous distribution name was LJMPython (v1.19 and older). It is now
labjack-ljm for the PyPi releases (v1.20 and newer). The namespace, package and
interface remain the same.


Installation Troubleshooting:

- If you have multiple versions of Python installed, make sure you install for
  the Python version you will be using. For example, on Linux if both Python
  Python 2.7 and 3.5 are installed, you can install to Python 3.5 with:

      $ sudo python3.5 -m pip labjack-ljm install

- On Windows, if using the terminal/console and the pip command does not work,
  try:

      $ python -m pip labjack-ljm install

  If the python command cannot be found with an error of or similar to:

      'python' is not recognized as an internal or external command, operable
      program or batch file.

  That means either Python is not installed on your computer, or the Python
  executable path was not added to the Windows user or system path. To help
  resolve this issue, please run the Python Windows installer and in the
  "Customize Python" window, click the "Add python.exe to Path" option towards
  the bottom and select "Will be installed on local hard drive". Open a new
  terminal/console and retry installation.

- If you have LJMPython version 1.19 or older installed, and are updating to
  labjack-ljm v1.20 or newer, using pip for installation is recommended.

  If using the "python setup.py install" method to update, check the labjack.ljm
  version number afterwards.

  from labjack import ljm
  print(ljm.__version__)

  If it is not the version you installed, go to your Python installation's
  site-packeges directory. If you see a labjack_ljm-<DIST_VER>-py<PY_VER>.egg
  file (<DIST_VER> is labjack-ljm version and <PY_VER> is the Python version),
  delete the labjack directory. The egg file contains the labjack folder files
  zipped, and the labjack folder and its files will conflict with it.


Examples:

Example code can be found in the Examples directory.


Documentation:

LJM Python documentation can be found in the docstrings of the source code. The
source code files are located in the labjack/ljm directory.

Alternatively, after installation in Python you can use the help function on a
module for documentation. For example:

    $ python
    >>> from labjack import ljm
    >>> help(ljm.ljm)

LJM library documentation can be found here:

    https://labjack.com/support/software/api/ljm

T7 and T4 documentation can be found here:

    https://labjack.com/support/datasheets/t-series


License:

All LJM Python modules and examples are licensed under MIT X11. The license can
be found in the LICENSE.TXT file.
