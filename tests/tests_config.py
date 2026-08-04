# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

"""Test configuration module."""

from metainvenio.config import ConfigParser


def test_empty_conf(empty_ymlfp):
    """Test empty config generates empty-dict data."""
    conf = ConfigParser(empty_ymlfp)
    assert conf.data == {}


def test_orgs(conf):
    """Test organisations."""
    orgs = list(conf.organisations)
    assert len(orgs) == 1
    assert orgs[0].name == "myorg"


def test_repositories(conf):
    """Test repositories."""
    repos = conf.repositories
    assert [r.slug for r in repos] == ["myorg/testrepo", "myorg/anotherrepo"]


def test_single_repo(confrepo):
    """Test repositories."""
    repos = list(confrepo.repositories)
    assert [r.slug for r in repos] == [
        "myorg/testrepo",
    ]


def test_teams(conf):
    """Test teams."""
    teams = list(conf.teams)
    output = [
        (t.name, len(t.members), t.permission, len(t.repositories)) for t in teams
    ]
    assert output == [
        ("architects", 1, "admin", 2),
        ("maintainers", 2, "pull", 0),
        ("developers", 3, "push", 2),
        ("testrepo-maintainers", 2, "maintain", 1),
        ("anotherrepo-maintainers", 1, "maintain", 1),
    ]


def test_single_repo_teams(confrepo):
    """Test teams for single repo."""
    teams = list(confrepo.teams)
    assert [(t.name, len(t.members)) for t in teams] == [
        ("testrepo-maintainers", 2),
    ]
