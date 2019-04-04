labjack-ljm : LJM library Python wrapper for LabJack T7 and T4
04/03/2019
support@labjack.com


The Python wrapper package, modules and examples for the cross-platform LJM
library, which supports the LabJack T7 and T4.


Installation Requirements:

* Windows, Mac OS X / macOS, or Linux
* LJM library: https://labjack.com/support/software/installers/ljm
* Python 2.6, 2.7 and 3.x.


Installation:

After fulfilling the requirements, open a terminal/console and use pip to
install labjack-ljm for the first time:

python -m pip install labjack-ljm

To upgrade to a newer version use:

python -m pip install labjack-ljm --upgrade

On Linux and macOS, you can also install with pip like so:

pip install labjack-ljm

Alternatively, download the labjack-ljm distribution source, unzip the contents
and go to its unzipped directory. To install, run the the following command
(run with sudo on Linux and macOS):

    $ python setup.py install


Distribution Name Change:

The previous distribution name was LJMPython in versions v1.19 and older.
Starting with version 1.20 and the releases on PyPi, the distribution name is
labjack-ljm. The namespace, package and interface remain the same.


Installation Troubleshooting:

- If you have multiple versions of Python installed, make sure you install for
  the Python version you will be using. For example, on Linux if both Python
  Python 2.7 and 3.5 are installed, you can install to Python 3.5 with:

      $ python3.5 -m pip labjack-ljm install

- On Windows, if you have Python installed and installation of labjack-ljm fails
  with an error of, or similar to:

      'python' is not recognized as an internal or external command, operable
      program or batch file.

  The Python executable path may not have been added to the Windows user or
  system path. One way to add Python to the path is to run the Python Windows
  installer and in the "Customize Python" window click the "Add python.exe to
  Path" option towards the bottom and select "Will be installed on local hard
  drive". Afterwards, open a new terminal/console and retry labjack-ljm
  installation.

- If you have LJMPython version 1.19 or older installed, and are updating to
  labjack-ljm v1.20 or newer, using pip for installation is recommended.

  If using setup.py for installation, afterwards check the labjack.ljm version
  number.

  from labjack import ljm
  print(ljm.__version__)

  If it is not the version you installed and still reports a previous version,
  go to your Python site-packeges directory. If you see a
  labjack_ljm-<DIST_VER>-py<PY_VER>.egg file (<DIST_VER> is labjack-ljm version
  and <PY_VER> is the Python version), delete the labjack directory. The egg
  file contains the labjack folder files zipped, and the labjack folder and its
  files are conflicting.


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
