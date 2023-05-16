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

"""Configuration file parser."""

import yaml
from attrdict import AttrDict


class ConfigParser(object):
    """MetaInvenio configuration file parser."""

    def __init__(self, fp, repository=None, repository_type=None):
        """Parse configuration file."""
        self.select_repo = repository
        self.select_type = repository_type
        self.data = yaml.load(fp) or {}

    @property
    def organisations(self):
        """Iterator over organisations."""
        for org_name, org in self.data.get('orgs', {}).items():
            org.update({'name': org_name})
            yield AttrDict(org)

    @property
    def teams(self):
        """Iterator over teams."""
        repos_list = [r.name for r in self.repositories]

        for org in self.organisations:
            if not self.select_repo:
                for name, data in org.get('teams', {}).items():
                    data['org'] = org
                    data['name'] = name
                    data['is_repo_team'] = False
                    data.setdefault('repositories', [])
                    data.setdefault('permission', 'pull')
                    if data['repositories'] == '*':
                        data['repositories'] = repos_list
                    yield AttrDict(data)

        for repo in self.repositories:
            if not repo.team:
                continue
            maintainers = repo.get('maintainers', [])
            yield AttrDict({
                'name': repo.team,
                'members': maintainers,
                'org': org,
                'repositories': [repo.name],
                'permission': 'maintain',
                'is_repo_team': True,
            })

    def is_selected(self, repo):
        """Determine if repository is selected."""
        if self.select_repo:
            return repo['slug'] in self.select_repo
        elif self.select_type:
            return repo.get('type', None) in self.select_type
        else:
            return True

    @property
    def repositories(self):
        """Iterator over repositories."""
        for org in self.organisations:
            for repo_name, repo in org.repositories.items():
                repo['name'] = repo_name
                repo['org'] = org
                repo['slug'] = '{}/{}'.format(org.name, repo_name)
                if self.is_selected(repo):
                    repo.setdefault('pypi', True)
                    repo.setdefault('branches', ['master'])
                    repo.setdefault('i18n', True)
                    repo.setdefault('has_issues', True)
                    repo.setdefault('has_wiki', False)
                    repo.setdefault('allow_merge_commit', False)
                    repo.setdefault('allow_rebase_merge', True)
                    repo.setdefault('allow_squash_merge', True)
                    repo.setdefault('default_branch', 'master')
                    repo.setdefault('team', '{}-maintainers'.format(repo_name))
                    repo.setdefault('maintainers', [])
                    repo.setdefault(
                        'url', 'https://{}.readthedocs.io'.format(repo_name))
                    yield AttrDict(repo)
