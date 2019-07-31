# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2017-2019 CERN.
#
# Invenio is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration."""

from __future__ import absolute_import, print_function

from os.path import dirname, join

import pytest

from metainvenio.config import ConfigParser


@pytest.yield_fixture()
def ymlfp():
    """File pointer to YAML configuration file."""
    fp = open(join(dirname(__file__), 'repositories.yml'), 'r')
    yield fp
    fp.close()


@pytest.fixture()
def empty_ymlfp():
    """File pointer to YAML configuration file."""
    return ''


@pytest.fixture()
def conf(ymlfp):
    """Test configuration."""
    return ConfigParser(ymlfp)


@pytest.fixture()
def confrepo(ymlfp):
    """Test configuration for single repository."""
    return ConfigParser(ymlfp, repository='myorg/testrepo')
