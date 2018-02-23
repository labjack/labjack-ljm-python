from distutils.core import setup
setup(name='LJMPython',
      version='1.18.0',
      description='The LJM Python package for the LabJack T4 and T7.',
      url='https://labjack.com/support/software/examples/ljm/python',
      author='LabJack Corporation',
      author_email="support@labjack.com",
      license='MIT X11',
      packages=['labjack', 'labjack.ljm']
      )
