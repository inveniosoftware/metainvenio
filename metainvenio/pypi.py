# SPDX-FileCopyrightText: 2019-2023 CERN.
# SPDX-License-Identifier: MIT

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
