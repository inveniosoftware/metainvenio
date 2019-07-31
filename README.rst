..
    This file is part of Invenio.
    Copyright (C) 2017-2019 CERN.

    Invenio is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.


=============
 MetaInvenio
=============

.. image:: https://img.shields.io/travis/inveniosoftware/metainvenio.svg
        :target: https://travis-ci.org/inveniosoftware/metainvenio

.. image:: https://img.shields.io/coveralls/inveniosoftware/metainvenio.svg
        :target: https://coveralls.io/r/inveniosoftware/metainvenio

.. image:: https://img.shields.io/pypi/v/metainvenio.svg
        :target: https://pypi.org/pypi/metainvenio

CLI management tool for Invenio projects.

Based on a YAML file configuration, this CLI tool will manage e.g.:

* GitHub:
    * Organisation teams, their members and repository permissions.
    * Repository settings, MAINTAINERS file, branch protection (with push
      access restricted to a team of maintainers for the repository).
* Travis:
    * Hook enabled/disabled state.
    * Build status/triggering
    * Cron jobs
    * Encryption (for e.g. PyPI deployment section in ``.travis.yml``).

**Example usage:**

You setup your configuration in a YAML file similar to this:

.. code-block:: yaml

    orgs:
      myorg:
        teams:
          architects:
            permissions: admin
            repositories: "*"
            members:
              - usera
        repositories:
          myrepo:
            description: My best repo ever.
            maintainers:
            - usera
            - userb

Then provide the YAMl file to the tool and run e.g.:

.. code-block:: console

    $ metainvenio -c conf.yml github -t <token> teams-sync
    $ metainvenio -c conf.yml github -t <token> repos-configure

Further documentation is available on https://metainvenio.readthedocs.io/
