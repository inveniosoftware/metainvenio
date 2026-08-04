# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

"""Command line interface for MetaInvenio."""

import click
import yaml
from attrdict import AttrDict

from .conf import conf
from .github import github
from .main import cli
from .pypi import pypi
