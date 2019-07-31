# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""PyPI CLI."""

from __future__ import absolute_import, print_function

import click

from ..pypi import PyPIAPI
from .main import cli


@cli.group()
@click.pass_context
def pypi(ctx):
    """Repository management for PyPI."""
    ctx.obj['client'] = PyPIAPI()


@pypi.command('latest-release')
@click.pass_context
def pypi_latest_release(ctx):
    """Ensure Travis is enabled/disabled."""
    conf = ctx.obj['config']
    pypi = ctx.obj['client']

    for repo in conf.repositories:
        if not getattr(repo.travis, 'pypideploy', False):
            click.echo(
                '{}: '.format(repo.slug) +
                click.style('skipped', fg='yellow')
            )
            continue
        data = pypi.latest_release(repo.name)
        if not data:
            click.echo(
                '{}: '.format(repo.slug) +
                click.style('failed', fg='red')
            )
        else:
            status = pypi.development_status(data['info']['classifiers'])
            click.echo('{repo}: {version} ({status})'.format(
                    repo=repo.slug,
                    version=data['info']['version'],
                    status=status,
                )
            )
