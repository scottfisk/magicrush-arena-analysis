# magicrush-arena-analysis
An analysis of relative power for magicrush arena teams

Prerequisites
-------------

1. Python 3.X

   - [Installing Python on Mac OS X](http://docs.python-guide.org/en/latest/starting/install/osx/)
   - [Installing Python on Windows](http://docs.python-guide.org/en/latest/starting/install/win/)
   - [Installing Python on Linux](http://docs.python-guide.org/en/latest/starting/install/linux/)

   Also install [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/):

   - Mac and Linux

     ```bash
     $ pip install virtualenvwrapper
     $ echo "source /usr/local/bin/virtualenvwrapper.sh" >> ~/.bashrc
     ```

2. Numpy
   - [Use distro package if available](http://www.scipy.org/install.html)

Installing
----------

1. Set up a new virtual environment

   ```bash
   $ mkvirtualenv --system-site-packages magicrush
   ```

2. Install requirements

   ```bash
   $ pip install -r requirements.txt
   ```
