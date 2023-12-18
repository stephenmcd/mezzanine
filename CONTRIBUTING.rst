Thank you for your interest in contributing to this project!

* If you're confident you've identified a bug, or have already written a
  patch, feel free to open an issue or pull request. Otherwise, please discuss
  on the `mezzanine-users <http://groups.google.com/group/mezzanine-users/topics>`_ mailing list first.
* For large features or bug fixes it's always a good idea to open an issue before you start developing your solution. This way the right approach and ideas can be discussed upfront instead of after spending time and energy developing it.
* Contributions must be made available on a separately named branch,
  based on the latest version of the master branch.
* If you are adding new functionality, you must include basic tests
  and documentation.
* Please add your name to the end of the AUTHORS file as part of your pull
  request.

Testing
-------

After cloning the repository and working on your contribution, install the extra testing requirements and run ``pytest``.

.. code-block:: bash

    pip install -e ".[testing]"
    pytest

Since the test suite is quite big you may want to run only a specific test case:

.. code-block:: bash

    # Test the "galleries" app only
    pytest tests/test_galleries.py

Code Style
----------

Python code style is enforced with ``flake8`` and  ``black``. You can install and run both as follows:

.. code-block:: bash

  pip install -e ".[codestyle]"
  black . --check # Omit the flag to have black autofix errors
  flake8 .

If your editor is configured to integrate with ``black`` and ``flake8`` it should pick up the project's configuration automatically.

Continous Integration
---------------------

When you are ready to contribute your changes `create and submit a pull request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`_ against the ``master`` branch. This will run all tests in all supported Python and Django versions and alert you if any of them fail.
