astrobase_services
=============
This module contains a service that contains several AstroBase services.

See 'astrobase_services -h' for help and 'astrobase_services -e' for examples.

This package is required when using atdb_services

Installing
^^^^^^^^^^
To install a version from Nexus repository use::

    > pip install <<nexus url>> --upgrade
    or download and install the tarball,
    > pip install atdb_interface.tar.gz --upgrade

Within the development environment such as with PyCharm one can install the package within the virtualenv with which
PyCharm is configured. To avoid uninstall and install after each code change pip can install packages within development
mode::

    (.env) > pip install -e ..project../atdb_services_pip --upgrade

This will install the package with soft links to the original code, such that one gets immediate refresh within PyCharm,
which is used for refactoring, code completion, imports etc.

Uninstalling
^^^^^^^^^^^^
Uninstall is trivial using the command (watch out for the '-')::

    > pip uninstall atdb-services

or without confirmation::

    > pip uninstall --yes atdb-services