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
@click.option('--token', '-t', help='Travis token', default='')
@click.option('--ghtoken', '-gt', help='GitHub token', default='')
@click.pass_context
def travis(ctx, token, ghtoken):
    """Repository management for Travis."""
    if not token:
        ghauth = None
        if not ghtoken:
            # Help user obtain a Travis access token.
            click.secho(
                'You need a Travis API access token. You get it from a '
                'temporary GitHub token. See '
                'https://docs.travis-ci.com/api#authentication. We will now '
                'help you obtain the token and need your GitHub '
                'username and password for that. If you dont feel confident '
                'providing that, simply follow instrcutions on above link.\n',
                fg='yellow'
            )

            # Query for GitHub username, password and two-factor code if needed
            def callback_2fa():
                code = ''
                while not code:
                    code = click.prompt('Enter 2FA code', type=str)
                return code

            user = click.prompt('GitHub username', type=str)
            password = click.prompt(
                'GitHub password', type=str, hide_input=True)
            scopes = [
                'read:org', 'user:email', 'repo_deployment',
                'repo:status', 'public_repo', 'write:repo_hook'
            ]

            # Create temporary GitHub token.
            gh = login(user, password, two_factor_callback=callback_2fa)
            ghauth = gh.authorize(
                user, password, scopes=scopes,
                note='Travis CI temporary token')
            ghtoken = ghauth.token

        # Exchange GitHub token for Travis token
        token = TravisPy.github_auth(
            ghtoken)._session.headers['Authorization'][len('token '):]

        if ghauth is not None:
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
@click.option('--password', '-p', help='PyPI password', prompt=True,
              hide_input=True)
@click.pass_context
def travis_pypi(ctx, user, password):
    """Create PyPI deployment section for repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        if not getattr(repo.travis, 'pypideploy', False):
            continue

        section = travis.pypi_deploy_section(
            repo.travis.pypideploy,
            user,
            travis.encrypt(repo.slug, password),
            i18n=repo.i18n,
        )
        click.secho('Deploy section for {}'.format(repo.slug), fg='green')
        click.echo(yaml.dump(section, default_flow_style=False))


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


@travis.command('cron-disable')
@click.pass_context
def travis_cron_disable(ctx):
    """Enable cron for repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        if repo.travis.active:
            continue

        if travis.cron_disable(repo.slug):
            click.secho(
                'Disabled crons for {}'.format(repo.slug), fg='green')
        else:
            click.secho(
                'Failed to disable crons for {}'.format(repo.slug),
                fg='red')


@travis.command('ghsync')
@click.pass_context
def travis_sync(ctx):
    """Sync list of GitHub repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']
    travis.v2client.user().sync()
    click.secho('Synchronizing list of GitHub repositories', fg='green')


@travis.command('build-status')
@click.option('--branch', '-b', help='Branch')
@click.option('--with-all-branches', '-a', help='All branches', is_flag=True)
@click.pass_context
def travis_build_status(ctx, branch=None, with_all_branches=False):
    """Get build status for default branch."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    statecolor = {
        'passed': 'green',
        'failed': 'red',
        'errored': 'red',
        'started': 'yellow',
        'created': 'yellow',
        'canceled': 'white',
    }

    for repo in conf.repositories:
        if not repo.travis.get('active', True):
            click.echo('{}: disabled'.format(repo.slug))
            continue

        if with_all_branches:
            branches = repo.branches
        elif branch:
            branches = [branch]
        else:
            branches = [repo.default_branch]

        for b in branches:
            build = travis.build_status(repo.slug, b)
            if build is None:
                click.secho('{}@{}: no build'.format(repo.slug, b), fg='red')
                continue
            click.echo(
                '{}@{}: '.format(repo.slug, b) +
                click.style(
                    build['state'],
                    fg=statecolor.get(build['state'], 'white')
                ) +
                ' ({})'.format(build['started_at'])
            )


@travis.command('build-request')
@click.option('--branch', '-b', help='Branch')
@click.option('--repos', '-r', type=click.STRING, help='Comma separated ' +
                                                       'list of GitHub ' +
                                                       'repositories names')
@click.pass_context
def travis_build_request(ctx, branch=None, repos=None):
    """Trigger a new build on default branch of all repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    repositories = conf.repositories
    if repos:
        repos = [r.strip() for r in repos.split(',')]
        repositories = filter(lambda r: r['name'] in repos, repositories)

    for repo in repositories:
        if not repo.travis.get('active', True):
            click.echo('{}: disabled'.format(repo.slug))
            continue

        branch = branch or repo.default_branch
        if travis.build_request(repo.slug, branch):
            click.echo(
                '{}@{}: '.format(repo.slug, branch) +
                click.style('requested', fg='green')
            )
        else:
            click.echo(
                '{}@{}: '.format(repo.slug, branch) +
                click.style('failed', fg='red')
            )


@travis.command('encrypt')
@click.option('--value', '-v', help='Value to encrypt', prompt=True,
              hide_input=True)
@click.pass_context
def travis_encrypt(ctx, value):
    """Encrypt the same value for multiple repositories."""
    conf = ctx.obj['config']
    travis = ctx.obj['client']

    for repo in conf.repositories:
        if not repo.travis.active:
            continue
        encrypted_value = travis.encrypt(repo.slug, value)
        click.echo('{}: {}'.format(repo.slug, encrypted_value))
