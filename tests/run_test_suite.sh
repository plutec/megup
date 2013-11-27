#!/bin/bash                                                                                                                     
# This script runs the entire test suite. At the moment, all it does is make
# use of nostests. It has been added so that developers know *what* to use
# when they want to run the test suite.

nosetests -sv .
