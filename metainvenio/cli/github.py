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
from github3 import GitHub

from ..github import OrgAPI, RepositoryAPI
from .main import cli


@cli.group()
@click.option('--token', '-t', help='GitHub token', prompt=True)
@click.pass_context
def github(ctx, token):
    """Repository management for GitHub."""
    ctx.obj['client'] = GitHub(token=token)


@github.command('repos-configure')
@click.option('--with-maintainers-file', is_flag=True)
@click.pass_context
def github_repo_configure(ctx, with_maintainers_file=False):
    """Configure GitHub repositories."""
    conf = ctx.obj['config']
    gh = ctx.obj['client']

    for repo in conf.repositories:
        click.echo('Configuring {}'.format(repo.slug))
        repoapi = RepositoryAPI(gh, conf=repo)
        if repoapi.update_settings():
            click.echo('Updated settings')
        if repoapi.update_team():
            click.echo('Updated maintainer team')
        if repoapi.update_branch_protection():
            click.echo('Updated branch protection')
        if with_maintainers_file:
            click.echo('Checking MAINTAINERS file')
            if repoapi.update_maintainers_file():
                click.echo('Updated MAINTAINERS file')
        # TODO prevent merge commits


@github.command('teams-sync')
@click.pass_context
def github_teams_sync(ctx):
    """Synchronize GitHub teams."""
    conf = ctx.obj['config']
    gh = ctx.obj['client']

    for org in conf.organisations:
        click.echo('Configuring {} teams'.format(org.name))
        orgapi = OrgAPI(gh, conf=org)
        if orgapi.update_teams([t for t in conf.teams if t.org == org]):
            click.echo('Updated organisation teams')


@github.command('repos-conf-check')
@click.pass_context
def github_repo_list(ctx):
    """List repositories in organisations."""
    conf = ctx.obj['config']
    gh = ctx.obj['client']

    for org in conf.organisations:
        orgapi = OrgAPI(gh, conf=org)

        ghrepos = set([r.name for r in orgapi.repos()])
        confrepos = set(org.repositories.keys())
        added = ghrepos - confrepos
        removed = confrepos - ghrepos

        if added:
            click.secho(
                'Missing {} repositories'.format(org.name), fg='yellow')
            for r in sorted(added):
                click.echo(r)
        if removed:
            click.secho(
                'Removed {} repositories'.format(org.name), fg='yellow')
            for r in sorted(removed):
                click.echo(r)
        if not added and not removed:
            click.secho(
                'Configuration for {} in sync'.format(org.name), fg='green')


@github.command('yaml-template')
@click.pass_context
def github_yaml_template(ctx):
    """Generate YAML template of repositories."""
    conf = ctx.obj['config']
    gh = ctx.obj['client']

    data = {'orgs': {}}

    for org in conf.organisations:
        click.secho('Fetching data for {}'.format(org.name), fg='green')
        orgapi = OrgAPI(gh, conf=org)
        data['orgs'][org.name] = orgapi.yaml_template()

    click.echo(yaml.safe_dump(
        data,
        allow_unicode=True,
        default_flow_style=False,
    ))
