..
    SPDX-FileCopyrightText: 2017 CERN.
    SPDX-License-Identifier: MIT

=============
 MetaInvenio
=============

.. image:: https://img.shields.io/coveralls/inveniosoftware/metainvenio.svg
        :target: https://coveralls.io/r/inveniosoftware/metainvenio

.. image:: https://img.shields.io/github/tag/inveniosoftware/metainvenio.svg
        :target: https://github.com/inveniosoftware/metainvenio/releases

.. image:: https://img.shields.io/pypi/dm/metainvenio.svg
        :target: https://pypi.python.org/pypi/metainvenio

.. image:: https://img.shields.io/github/license/inveniosoftware/metainvenio.svg
        :target: https://github.com/inveniosoftware/metainvenio/blob/master/LICENSE

CLI management tool for Invenio projects.

Based on a YAML file configuration, this CLI tool will manage e.g.:

* GitHub:
    * Organisation teams, their members and repository permissions.
    * Repository settings, MAINTAINERS file, branch protection (with push
      access restricted to a team of maintainers for the repository).

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
