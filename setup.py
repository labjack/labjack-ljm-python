from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX :: Linux',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Topic :: Software Development',
    'Topic :: Software Development :: Embedded Systems',
    'Topic :: System :: Hardware'
    ]

setup(name="labjack-ljm",
      version='1.20.0',
      description='LJM library Python wrapper for LabJack T7 and T4.',
      url='https://labjack.com/support/software/examples/ljm/python',
      author='LabJack Corporation',
      author_email="support@labjack.com",
      maintainer='LabJack Corporation',
      maintainer_email='support@labjack.com',
      classifiers=CLASSIFIERS,
      license='MIT X11',
      packages=['labjack', 'labjack.ljm']
      )
