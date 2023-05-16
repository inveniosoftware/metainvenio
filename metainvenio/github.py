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

"""GitHub Maintainer API client."""

import logging
import re
from json import dumps

from attrdict import AttrDict
from github3 import GitHub
from github3.decorators import requires_auth
from github3.exceptions import NotFoundError
from github3.orgs import Organization, Team
from github3.repos import Repository
from github3.repos.branch import Branch

LINE_RE = re.compile('(.+)')

logger = logging.getLogger(__name__)


#
# GitHub API Extensions.
#
class ExtendedOrganization(Organization):
    """Organistaion extension."""

    @requires_auth
    def create_team(self, name, repo_names=[], privacy='closed'):
        """Create a new team and return it (with privacy support)."""
        data = {'name': name, 'repo_names': repo_names, 'privacy': privacy}
        url = self._build_url('teams', base_url=self._api)
        json = self._json(self._post(url, data), 201)
        return self._instance_or_null(Team, json)


class ExtendedTeam(Team):
    """Team extension."""

    @requires_auth
    def add_repository(self, repository, permission='pull'):
        """Add a repository to team (with support for permission)."""
        data = {'permission': permission}
        url = self._build_url('repos', repository, base_url=self._api)
        return self._boolean(self._put(url, data=dumps(data)), 204, 404)


class ExtendedRepository(Repository):
    """Branch extension."""

    def edit(self, name, description=None, homepage=None, private=None,
             has_issues=None, has_wiki=None, has_downloads=None,
             default_branch=None, allow_merge_commit=None,
             allow_rebase_merge=None, allow_squash_merge=None):
        """Edit this repository."""
        edit = {'name': name, 'description': description, 'homepage': homepage,
                'private': private, 'has_issues': has_issues,
                'has_wiki': has_wiki, 'has_downloads': has_downloads,
                'default_branch': default_branch,
                'allow_merge_commit': allow_merge_commit,
                'allow_rebase_merge': allow_rebase_merge,
                'allow_squash_merge': allow_squash_merge}

        self._remove_none(edit)
        json = None
        if edit:
            json = self._json(self._patch(self._api, data=dumps(edit)), 200)
            self._update_attributes(json)
            return True
        return False


class ExtendedBranch(Branch):
    """Branch extension."""

    def protect(self, required_status_checks=None,
                required_pull_request_reviews=None,
                required_linear_history=True,
                dismissal_restrictions=None,
                restrictions=None, enforce_admins=None):
        """Enable branch protection (with all features)."""
        data = {
            'required_status_checks': required_status_checks,
            'required_pull_request_reviews': required_pull_request_reviews,
            'dismissal_restrictions': dismissal_restrictions,
            'restrictions': restrictions,
            'enforce_admins': enforce_admins,
            'required_linear_history': required_linear_history,
        }

        url = self._build_url('protection', base_url=self._api)
        return self._json(
            self._put(url, data=dumps(data), headers=self.PREVIEW_HEADERS),
            200)


#
# Wrapper classes for GitHub API.
#
class GitHubAPI(object):
    """Base class for GitHub wrapper API classes."""

    def __init__(self, client, conf=None):
        """Initialize GitHub API."""
        self.conf = conf
        self.gh = client


class OrgAPI(GitHubAPI):
    """GitHub organisation API client."""

    @property
    def _ghorg(self):
        """Get the organisation client."""
        org = self.gh.organization(self.conf.name)
        return ExtendedOrganization(org.as_dict(), session=org.session)

    def repos(self):
        """List repositories."""
        return self._ghorg.repositories()

    def teams(self):
        """Get current organisation teams."""
        return (
            ExtendedTeam(t.as_dict(), session=t.session)
            for t in self._ghorg.teams()
        )

    def create_team(self, t):
        """Create a new GitHub team."""
        team = self._ghorg.create_team(
            t.name,
            repo_names=t.repositories,
        )
        return ExtendedTeam(team.as_dict(), session=team.session)

    @staticmethod
    def sync_team_members(team, members):
        """Sync team members."""
        updated = False
        current = {m.login for m in team.members()}
        expected = set(members)
        if expected != current:
            # Add/invite members
            for m in expected - current:
                team.invite(m)
                updated = True
            # Remove members
            for m in current - expected:
                team.revoke_membership(m)
                updated = True
        return updated

    def sync_team_repositories(self, team, permission, repositories):
        """Synchronize list of repositories for team."""
        updated = False
        ghrepos = {r.name: r for r in team.repositories()}

        current = set(ghrepos.keys())
        expected = set(repositories)
        old = current - expected
        new = expected - current
        existing = current & expected

        for r in old:
            team.remove_repository(ghrepos[r].full_name)
            updated = True

        for r in new:
            slug = '{}/{}'.format(self.conf.name, r)
            team.add_repository(slug, permission=permission)
            updated = True

        for r in existing:
            repo = ghrepos[r]
            if not repo.permissions.get(permission, False):
                team.add_repository(repo.full_name, permission=permission)
                updated = True

        return updated

    def update_teams(self, teams):
        """Update organisation teams."""
        updated = False
        current_teams = {t.name: t for t in self.teams()}
        expected_teams = {t.name: t for t in teams}

        # Detect team changes
        current = set(current_teams.keys())
        expected = set(expected_teams.keys())
        old = current - expected
        new = expected - current
        existing = current & expected

        # Delete old teams
        for t in old:
            team = current_teams[t]
            team.delete()
            updated = True

        # Create new teams
        for t in new:
            team = expected_teams[t]
            current_teams[t] = self.create_team(team)
            updated = True

        # Check existing teams
        for t in existing | new:
            expected_team = expected_teams[t]
            current_team = current_teams[t]

            if self.sync_team_members(current_team, expected_team.members):
                updated = True
            if self.sync_team_repositories(
                    current_team,
                    expected_team.permission,
                    expected_team.repositories):
                updated = True
        return updated

    def yaml_template(self):
        """Generate YAML template for organisation."""
        data = {'repositories': {}, 'teams': {}}

        repos = data['repositories']
        for r in self.repos():
            r = AttrDict(dict(org=self.conf, name=r.name))
            repos[r.name] = RepositoryAPI(self.gh, conf=r).yaml_template()
        return data


class RepositoryAPI(GitHubAPI):
    """Repository API."""

    @property
    def _ghrepo(self):
        repo = self.gh.repository(self.conf.org.name, self.conf.name)
        return ExtendedRepository(repo.as_dict(), session=repo.session)

    def update_settings(self):
        """Update repository settings."""
        repo = self._ghrepo

        is_dirty = any([
            repo.description != self.conf.description,
            repo.homepage != self.conf.url,
            repo.has_issues != self.conf.has_issues,
            repo.has_wiki != self.conf.has_wiki,
            repo.default_branch != self.conf.default_branch,
            repo.allow_merge_commit != self.conf.allow_merge_commit,
            repo.allow_rebase_merge != self.conf.allow_rebase_merge,
            repo.allow_squash_merge != self.conf.allow_squash_merge,
        ])

        if not is_dirty:
            return False

        res = repo.edit(
            self.conf.name,
            description=self.conf.description,
            homepage=self.conf.url,
            has_issues=self.conf.has_issues,
            has_wiki=self.conf.has_wiki,
            default_branch=self.conf.default_branch,
            allow_merge_commit=self.conf.allow_merge_commit,
            allow_rebase_merge=self.conf.allow_rebase_merge,
            allow_squash_merge=self.conf.allow_squash_merge,
        )
        if not res:
            raise RuntimeError(
                'Failed to update repository settings for {}'.format(
                    self.conf.name))
        return True

    def update_pull_req_template(self):
        """Update pull request template file."""
        filepath = '.github/pull_request_template.md'
        commit_message = 'global: pull request template update'

        content = self._get_dir_contents(filepath)
        with open(filepath, 'r') as f:
            template = f.read()
        if content:
            parsed = self._parse_pull_request_template(content)
            if parsed == template:
                return False
            content.update(commit_message, template)
        else:
            self._ghrepo.create_file(
                filepath, commit_message, template or b'\n')
        return True

    def update_maintainers_file(self):
        """Update maintainers file."""
        maintainers = "\n".join(sorted(self.conf.maintainers)).encode('utf8')
        commit_message = 'global: maintainers update'
        filepath = 'MAINTAINERS'

        contents = self._get_file_contents(filepath)
        if contents:
            # File exists, so check contents and update if needed.
            current_maintainers = self._parse_maintainers_file(contents)
            if set(current_maintainers) == set(self.conf.maintainers):
                return False
            contents.update(commit_message, maintainers)
        else:
            self._ghrepo.create_file(
                filepath, commit_message, maintainers or b'\n')
        return True

    def update_team(self):
        """Update repository team."""
        orgapi = OrgAPI(self.gh, conf=self.conf.org)

        # Find repository team.
        team = None
        for t in orgapi.teams():
            if t.name == self.conf.team:
                team = t

        # Create if team does not exists.
        updated = False
        if team is None:
            team = orgapi.create_team(AttrDict(dict(
                name=self.conf.team,
                repositories=[self.conf.name],
                permission='maintain',
            )))
            updated = True

        # Sync member/repo list if team exists
        if orgapi.sync_team_members(team, self.conf.maintainers):
            updated = True
        if orgapi.sync_team_repositories(team, 'maintain', [self.conf.name]):
            updated = True
        return updated

    def update_branch_protection(self):
        """Update branch protection."""
        repo = self._ghrepo
        for branch_name in self.conf.branches:
            branch = repo.branch(branch_name)
            branch = ExtendedBranch(branch.as_dict(), session=branch.session)
            branch.protect(
                required_status_checks=None,
                required_pull_request_reviews=None,
                required_linear_history=True,
                restrictions=dict(
                    users=[],
                    teams=[self.conf.team],
                ),
                dismissal_restrictions=dict(
                    users=[],
                    teams=[self.conf.team],
                ),
                enforce_admins=False,
            )
        return True

    def _get_file_contents(self, filepath):
        """Get content of a file."""
        contents = self._ghrepo.file_contents(filepath)
        if not bool(contents):
            return None
        return contents

    def _get_dir_contents(self, dirpath):
        try:
            directory = self._ghrepo.file_contents(dirpath)
            if not bool(directory):
                return None
            return directory
        except NotFoundError as e:
            return None

    @staticmethod
    def _parse_maintainers_file(contents):
        """Parse MAINTAINERS file."""
        lines = []
        for line in contents.decoded.decode('utf8').split('\n'):
            if not line.strip():
                continue
            m = LINE_RE.match(line)
            if not m:
                print('Failed to match: {}'.format(line))
                continue
            lines.append(m.group(1))
        return lines

    @staticmethod
    def _parse_pull_request_template(contents):
        return contents.decoded.decode('utf8')

    def yaml_template(self):
        """Generate a yaml template for a repository."""
        repo = self._ghrepo
        maintainers = []

        # Get maintainers from file.
        contents = self._get_file_contents('MAINTAINERS')
        if contents:
            maintainers = list(
                sorted(set(self._parse_maintainers_file(contents))))

        return {
            'type': '',
            'state': '',
            'description': (repo.description or u''),
            'maintainers': maintainers,
        }
