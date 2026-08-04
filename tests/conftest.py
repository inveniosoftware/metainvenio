# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

"""Pytest configuration."""

from os.path import dirname, join

import pytest

from metainvenio.config import ConfigParser


@pytest.yield_fixture()
def ymlfp():
    """File pointer to YAML configuration file."""
    fp = open(join(dirname(__file__), "repositories.yml"), "r")
    yield fp
    fp.close()


@pytest.fixture()
def empty_ymlfp():
    """File pointer to YAML configuration file."""
    return ""


@pytest.fixture()
def conf(ymlfp):
    """Test configuration."""
    return ConfigParser(ymlfp)


@pytest.fixture()
def confrepo(ymlfp):
    """Test configuration for single repository."""
    return ConfigParser(ymlfp, repository="myorg/testrepo")
