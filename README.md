#megup

[ Description ]

Backup system with mega service

In develop. Process at 2%. Not completly useful. You can contribute to the project! Welcome!

[ Configuration ]

The configuration file *should* be allocated in a file named "settings.conf"
allocated in the root directory of this project. Placing a different config
file in the current working directory from where you are using this script
*will not* overwrite these values.

If the environment variable $MEGUP_CONFIG_FILE is set, its content will be taken
as the path to the configuration file to be used. Therefore, any existing
configuration file in the root directory of this project will be ignored.
This is an addition specially targeted to developers. With this, you don't need
to modify the version-controlled settings.conf in order to use your own
configuration. You can keep a copy of this file in you home directory, and use
it by setting this variable:

    $ export MEGUP_CONFIG_FILE="/home/user/settings.conf"
    $ /home/user/megup/tests/run_test_suite.sh

[ Test Suite ]

If you're a developer playing around with this code and want to make sure you
haven't broken anything, you can run the test suite by running
`./tests/run_test_suite.sh`
