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
from github3 import login
from travispy import TravisPy

from ..travis import TravisAPI
from .main import cli


@cli.group()
@click.option('--token', '-t', help='Travis token', prompt=True, default='')
@click.pass_context
def travis(ctx, token):
    """Repository management for Travis."""
    if not token:
        # Help user obtain a Travis access token.
        click.secho(
            'You need a Travis API access token. You get it from a temporary '
            'GitHub token. See https://docs.travis-ci.com/api#authentication.'
            ' We will now help you obtain the token and need your GitHub '
            'username and password for that. If you dont feel confident '
            'providing that, simply follow instrcutions on above link.\n',
            fg='yellow'
        )

        # Query for GitHub username, password and two-factor code if needed.
        def callback_2fa():
            code = ''
            while not code:
                code = click.prompt('Enter 2FA code', type=str)
            return code

        user = click.prompt('GitHub username', type=str)
        password = click.prompt('GitHub password', type=str, hide_input=True)
        scopes = [
            'read:org', 'user:email', 'repo_deployment',
            'repo:status', 'public_repo', 'write:repo_hook'
        ]

        # Create temporary GitHub token.
        gh = login(user, password, two_factor_callback=callback_2fa)
        ghauth = gh.authorize(
            user, password, scopes=scopes, note='Travis CI temporary token')

        # Exchange GitHub token for Travis token
        token = TravisPy.github_auth(
            ghauth.token)._session.headers['Authorization'][len('token '):]

        # Delete GitHub token again
        ghauth.delete()

        click.secho('Your Travis token is: {}'.format(token), fg='green')

    ctx.obj['client'] = TravisAPI(token=token)


@travis.command('state-set')
@click.pass_context
def travis_state_set(ctx):
    """Ensure Travis is enabled/disabled."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        if repo.travis.active:
            travis.repo_enable(repo.slug)
            click.secho('Enabled {}'.format(repo.slug), fg='green')
        else:
            travis.repo_disable(repo.slug)
            click.secho('Disabled {}'.format(repo.slug), fg='green')


@travis.command('pypi')
@click.option('--user', '-u', help='PyPI user', prompt=True)
@click.option('--password', '-p', help='PyPI password', prompt=True)
@click.pass_context
def travis_pypi(ctx, user, password):
    """Create PyPI deployment section for repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        if not getattr(repo.travis, 'pypideploy', False):
            continue

        section = travis.pypi_deploy_section(
            conf.travis.pypideploy,
            user,
            travis.encrypt(repo.slug, password),
            i18n=repo.i18n,
        )
        click.secho('Deploy section for {}'.format(repo.slug), fg='green')
        click.echo(yaml.dump(section))


@travis.command('cron-list')
@click.pass_context
def travis_cron_list(ctx):
    """List crons for repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        crons = travis.crons(repo.slug)
        if not crons:
            click.secho('No crons for {}'.format(repo.slug), fg='yellow')
        else:
            click.secho('Crons for {}'.format(repo.slug), fg='green')
            for c in crons:
                click.echo('{} ({})'.format(c.branch.name, c.interval))


@travis.command('cron-enable')
@click.pass_context
def travis_cron_enable(ctx):
    """Enable cron for repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        for branch, interval in getattr(repo.travis, 'crons', {}).items():
            desc = 'cron for {}@{} {}'.format(repo.slug, branch, interval)
            try:
                travis.cron_enable(repo.slug, branch, interval=interval)
                click.echo('Enabled {}'.format(desc))
            except Exception as e:
                click.secho('Failed enabling {}'.format(desc), fg='red')
                click.echo(str(e))


@travis.command('ghsync')
@click.pass_context
def travis_sync(ctx):
    """Sync list of GitHub repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']
    travis.v2client.user().sync()
    click.secho('Synchronizing list of GitHub repositories', fg='green')
