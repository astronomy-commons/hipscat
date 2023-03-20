Contributing to hipscat
===============================================================================

Find (or make) a new GitHub issue
-------------------------------------------------------------------------------

Add yourself as the assignee on an existing issue so that we know who's working 
on what. If you're not actively working on an issue, unassign yourself.

If there isn't an issue for the work you want to do, please create one and include
a description.

You can reach the team with bug reports, feature requests, and general inquiries
by creating a new GitHub issue.

Create a branch
-------------------------------------------------------------------------------

It is preferable that you create a new branch with a name like 
``issue/##/<short-description>``. GitHub makes it pretty easy to associate 
branches and tickets, but it's nice when it's in the name.

Set up a development environment
-------------------------------------------------------------------------------

Most folks use conda for virtual environments. You may want to as well.

.. code-block:: bash

    $ git clone https://github.com/astronomy-commons/hipscat
    $ cd hipscat
    $ pip install -e .

.. tip::
    Installing on Mac

    Native prebuilt binaries for healpy on Apple Silicon Macs 
    `do not yet exist <https://healpy.readthedocs.io/en/latest/install.html#binary-installation-with-pip-recommended-for-most-other-python-users>`_, 
    so it's recommended to install via conda before proceeding to hipscat.

    .. code-block:: bash

        $ conda config --add channels conda-forge
        $ conda install healpy
        $ git clone https://github.com/astronomy-commons/hipscat
        $ cd hipscat
        $ pip install -e .
        
    When installing dev dependencies, make sure to include the single quotes.

    .. code-block:: bash
        
        $ pip install -e '.[dev]'

Testing
-------------------------------------------------------------------------------

Please add or update unit tests for all changes made to the codebase. You can run
unit tests locally simply with:

.. code-block:: bash

    pytest

If you're making changes to the sphinx documentation (anything under ``docs``),
you can build the documentation locally with a command like:

.. code-block:: bash

    cd docs
    make html

Create your PR
-------------------------------------------------------------------------------

Please use PR best practices, and get someone to review your code.

We have a suite of continuous integration tests that run on PR creation. Please
follow the recommendations of the linter.

Merge your PR
-------------------------------------------------------------------------------

The author of the PR is welcome to merge their own PR into the repository.

Optional - Release a new version
-------------------------------------------------------------------------------

Once your PR is merged you can create a new release to make your changes available. 
GitHub's `instructions <https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`_ 
for doing so are here. 
Use your best judgement when incrementing the version. i.e. is this a major, minor, or patch fix.