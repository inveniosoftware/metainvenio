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

"""Travis API client."""

from __future__ import absolute_import, print_function

import argparse
import base64
import copy

import requests
from attrdict import AttrDict
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from travispy import TravisPy
from travispy._helpers import get_response_contents

from .version import __version__

try:
    from urllib.parse import quote_plus
except ImportError:
    from urllib import quote_plus


V2URI = 'https://api.travis-ci.org/'
V3URI = 'https://api.travis-ci.org/v3'


class TravisAPI(object):
    """Travis API client."""

    def __init__(self, token=None, github_token=None):
        """Initialize Travis API."""
        assert github_token or token
        self._github_token = github_token
        self._travis_token = token

    @property
    def cache(self):
        """Special property used by methods to cache objects."""
        if not hasattr(self, '_cache'):
            self._cache = {
                'repos': {},
            }
        return self._cache

    @property
    def v2client(self):
        """Travis API v2 client."""
        if self._travis_token:
            return TravisPy(token=self._travis_token)
        else:
            return TravisPy.github_auth(self._github_token)

    @property
    def v3client(self):
        """Travis API v3 client."""
        if not hasattr(self, '_v3session'):
            token_header = self.v2client._session.headers['Authorization']
            self._v3session = requests.Session()
            self._v3session.headers.update({
                'User-Agent': 'MetaInvenio/{}'.format(__version__),
                'Accept': 'application/json',
                'Authorization': token_header,
            })
        return self._v3session

    def repo(self, repo_slug):
        """Get repository."""
        if repo_slug not in self.cache['repos']:
            self.cache['repos'][repo_slug] = self.v2client.repo(repo_slug)
        return self.cache['repos'][repo_slug]

    def repo_enable(self, repo_slug):
        """Enable repository."""
        repo = self.repo(repo_slug)
        repo.enable()

    def repo_disable(self, repo_slug):
        """Disable repository."""
        repo = self.repo(repo_slug)
        repo.disable()

    def repo_key(self, repo_slug):
        """Get repository public key."""
        s = self.v2client._session
        endpoint = '{}/repos/{}/key'.format(s.uri, repo_slug)
        res = s.get(endpoint)
        if res.status_code == 200:
            return res.json()['key']
        else:
            res = s.post(endpoint)
            return res.json()['key'] if res.status_code == 200 else None

    def crons(self, repo_slug):
        """List enabled crons."""
        repo_id = self.repo(repo_slug).id
        res = self.v3client.get('{}/repo/{}/crons'.format(V3URI, repo_id))
        return (AttrDict(c) for c in get_response_contents(res)['crons'])

    def cron_enable(self, repo_slug, branch, interval='weekly',
                    dont_run_if_recent_build_exists=True):
        """Enable cron for specific branc on a repository."""
        repo_id = self.repo(repo_slug).id
        endpoint = '{}/repo/{}/branch/{}/cron'.format(V3URI, repo_id, branch)
        res = self.v3client.post(endpoint, json={
            'interval': interval,
            'dont_run_if_recent_build_exists': True,
        })
        return get_response_contents(res)

    def cron_disable(self, repo_slug):
        """Disable all cron jobs for a repository."""
        for cron in self.crons(repo_slug):
            res = self.v3client.delete('{}/cron/{}'.format(V3URI, cron.id))
            if res.status_code != 204:
                return False
        return True

    def encrypt(self, repo_slug, value):
        """Encrypt value using a repository's public key."""
        key = RSA.importKey(self.repo_key(repo_slug))
        cipher = PKCS1_v1_5.new(key)
        return base64.b64encode(
            cipher.encrypt(value.encode('utf8'))
        ).decode('utf8')

    def pypi_deploy_section(self, template, user, secure_password, i18n=True):
        """Generate PyPI deploy section."""
        template = copy.deepcopy(dict(template))
        template['user'] = user
        template['password'] = {'secure': secure_password}
        if i18n:
            template['distributions'] = 'compile_catalog sdist bdist_wheel'
        else:
            template['distributions'] = 'sdist bdist_wheel'
        return template

    def build_status(self, repo_slug, branch):
        """Get travis build status for a branch."""
        endpoint = '{}/repo/{}/builds'.format(V3URI, quote_plus(repo_slug))
        res = self.v3client.get(
            endpoint,
            params={'branch.name': branch, 'limit': 1}
        )
        try:
            return res.json()['builds'][0] if res.status_code == 200 else None
        except IndexError:
            return None

    def build_request(self, repo_slug, branch):
        """Request a travis build of branch."""
        endpoint = '{}/repo/{}/requests'.format(V3URI, quote_plus(repo_slug))
        res = self.v3client.post(
            endpoint,
            params={'request': {'branch': branch}}
        )
        return res.status_code == 202
