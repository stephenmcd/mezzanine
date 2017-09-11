Please note the following instructions for opening an issue:

* If you're confident you've identified a bug, or have already written a
  patch, feel free to open an issue or pull request. Otherwise, please discuss
  on the `mezzanine-users <http://groups.google.com/group/mezzanine-users/topics>`_ mailing list first.
* Contributed code must be written in the existing style. For Python
  (and to a decent extent, JavaScript as well), this is as simple as
  following the `Django coding style <https://docs.djangoproject.com/en/dev/internals/contributing/writing-code/coding-style/>`_ and (most importantly)
  `PEP 8 <http://www.python.org/dev/peps/pep-0008/>`_. Front-end CSS should adhere to the
  `Bootstrap CSS guidelines <https://github.com/twbs/bootstrap/blob/master/CONTRIBUTING.md#css>`_.
* Contributions must be made available on a separately named branch,
  based on the latest version of the master branch.
* Run the tests before committing your changes. If your changes
  cause the tests to break, they won't be accepted.

  Tests can be run using::

    ./setup.py test

  Or specified tests using::

    ./mezzanine/bin/runtests.py mezzanine.core.tests.CoreTests

* If you are adding new functionality, you must include basic tests
  and documentation.
* Please add your name to the end of the AUTHORS file as part of your pull
  request.
