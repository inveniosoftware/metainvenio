# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017 CERN.
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

"""Configuration commands."""

from __future__ import absolute_import, print_function

import click
import yaml
from attrdict import AttrDict

from .main import cli


def _maintainer_row(maintainers, selected):
    row = []
    for m in maintainers:
        if m in selected:
            row.append('x')
        else:
            row.append('')
    return row


@cli.group()
def conf():
    """Configuration helpers."""


@conf.command('repo-overview')
@click.pass_context
def conf_repo_overview(ctx):
    """Repositories overview as CSV."""
    conf = ctx.obj['config']

    # Extract list of maintainers.
    maintainers = set()
    for repo in conf.repositories:
        maintainers.update(repo.maintainers)
    maintainers = list(sorted(maintainers))

    # Write header.
    click.echo(','.join([
        'Name',
        'Type,'
        'State',
        '# Maintainers',
    ] + maintainers))

    for repo in conf.repositories:
        click.echo(','.join([
            repo.name,
            repo.type,
            repo.state,
            str(len(repo.maintainers)),

        ] + _maintainer_row(maintainers, repo.maintainers)))
