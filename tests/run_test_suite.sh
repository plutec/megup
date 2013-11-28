#!/bin/bash                                                                                                                     
# This script runs the entire test suite. At the moment, all it does is make
# use of nostests. It has been added so that developers know *what* to use
# when they want to run the test suite.

nosetests -sv .


# Import end-to-end scripts
own_dir="$(dirname "$0")"
for f in $own_dir/end_to_end/test-*.sh; do
    source $f
done


# Run all existing end-to-end tests
echo "-- END-TO-END Tests Results --"
cd $own_dir/..  # Necessary for tests to have immediate access to main.py

ret=0
for t in $(declare -F | awk '/ test_/ {print $3}'); do
    echo -n "$t ... "
    $t >/dev/null 2>&1
    [[ $? == 0 ]] && echo "PASSED" || {
	echo "FAILED";
        ret=1;
    }
done
exit $ret
