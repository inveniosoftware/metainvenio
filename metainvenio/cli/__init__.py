# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Command line interface for MetaInvenio."""

from __future__ import absolute_import, print_function

import click
import yaml
from attrdict import AttrDict

from .conf import conf
from .github import github
from .main import cli
from .pypi import pypi
from .travis import travis
