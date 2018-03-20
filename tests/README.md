Plumage unit tests
==================
This directory contains the unit tests for Plumage. It is organized pretty much along the lines recommended in Kenneth Reitz's [_The Hitchhiker’s Guide to Python_](http://docs.python-guide.org/en/latest/), in the section "[Structuring Your Project](http://docs.python-guide.org/en/latest/writing/structure/)".

There are three tests:

  `basic.py`: imports Plumage and instantiates an empty TSDRReq class, but nothing more  
  `test_offline.py`: tests Plumage entirely offline, using the supplied test files. No network contact with the USPTO  
  `test_online.py`: tests Plumage online, using the data obtained over the network from the USPTO  

The tests are designed to be bilingual Python, i.e. the support both Python2 and Python3. To test with both
versions of Python, call the desired Python interpreter directly, e.g:

On Linux, use one or more of the following, depending on how Python is installed on your system:  
  `$ python test_offline.py`                  _(default Python)_  
  `$ python2 test_offline.py`                 _(Python 2)_  
  `$ python3 test_offline.py`                 _(Python 3)_  
  `$ /usr/local/bin/python test_offline.py`    _(default Python)_   
  `$ /usr/local/bin/python2 test_offline.py`  _(Python 2)_  
  `$ /usr/local/bin/python2 test_offline.py`  _(Python 3)_  

On Windows, use the following:  
  `> python test_offline.py`                  _(default Python)_  
If you have both Python 2 and 3 installed, and want to test with both, the [Python Launcher](https://www.python.org/dev/peps/pep-0397/) is recommended:  
  `> py -2 test_offline.py`                  _(Python 2)_  
  `> py -3 test_offline.py`                  _(Python 3)_    


