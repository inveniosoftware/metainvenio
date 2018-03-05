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

"""Command line interface for MetaInvenio."""

from __future__ import absolute_import, print_function

import click
import yaml
from attrdict import AttrDict

from ..config import ConfigParser


@click.group()
@click.option(
    '--config', '-c', help='Configuration file path.', type=click.File(),
    required=True)
@click.option('--repository', '-r', help='Repository slug', default=None, multiple=True)
@click.option('--repository-type', '-t', help='Repository type', default=None, multiple=True)
@click.pass_context
def cli(ctx, config, repository=None, repository_type=None):
    """Management tools for Invenio modules."""
    ctx.obj = AttrDict({'config': ConfigParser(
        config,
        repository=repository,
        repository_type=repository_type,
    )})
