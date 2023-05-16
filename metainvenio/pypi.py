# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2019-2023 CERN.
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

"""PyPI API."""

import requests


class PyPIAPI(object):
    """Python Package Index API client."""

    def __init__(self):
        """Initialize API class."""
        self.client = requests.Session()

    def latest_release(self, package_name):
        """Get information about latest release for a given package."""
        endpoint = "https://pypi.org/pypi/{}/json".format(package_name)
        res = self.client.get(endpoint)
        if res.status_code == 200:
            return res.json()
        return None

    @staticmethod
    def development_status(classifiers):
        """Find development status classifier."""
        for c in classifiers:
            parts = [x.strip() for x in c.split("::")]
            if parts[0] == "Development Status":
                return parts[1]
        return "Unknown"
