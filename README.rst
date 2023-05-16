..
    This file is part of Invenio.
    Copyright (C) 2017 CERN.

    Invenio is free software; you can redistribute it
    and/or modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 2 of the
    License, or (at your option) any later version.

    Invenio is distributed in the hope that it will be
    useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Invenio; if not, write to the
    Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
    MA 02111-1307, USA.

    In applying this license, CERN does not
    waive the privileges and immunities granted to it by virtue of its status
    as an Intergovernmental Organization or submit itself to any jurisdiction.

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
