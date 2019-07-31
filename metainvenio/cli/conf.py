# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

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
