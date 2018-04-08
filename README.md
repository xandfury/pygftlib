Gevent based simple File Transfer Library

Two applications (written in python) - one reads a file and sends it over the network to the other application,
which stores the file into its CWD. How would you do it (without using a framework that already does this)?
L4 protocol of choice would be UDP, the reliability part is _your_ duty