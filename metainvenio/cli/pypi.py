# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.

"""PyPI CLI."""

from __future__ import absolute_import, print_function

import click

from ..pypi import PyPIAPI
from .main import cli


@cli.group()
@click.pass_context
def pypi(ctx):
    """Repository management for PyPI."""
    ctx.obj["client"] = PyPIAPI()


@pypi.command("latest-release")
@click.pass_context
def pypi_latest_release(ctx):
    """Get latest release."""
    conf = ctx.obj["config"]
    pypi = ctx.obj["client"]

    for repo in conf.repositories:
        data = pypi.latest_release(repo.name)
        if not data:
            click.echo("{}: ".format(repo.slug) + click.style("failed", fg="red"))
        else:
            status = pypi.development_status(data["info"]["classifiers"])
            release = data["releases"][data["info"]["version"]][0]
            click.echo(
                "{repo}: {version} ({status} - {release_date})".format(
                    repo=repo.slug,
                    version=data["info"]["version"],
                    status=status,
                    release_date=release["upload_time"][:10],
                )
            )
