# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

"""Configuration commands."""

import click

from .main import cli


def _maintainer_row(maintainers, selected):
    row = []
    for m in maintainers:
        if m in selected:
            row.append("x")
        else:
            row.append("")
    return row


@cli.group()
def conf():
    """Configuration helpers."""


@conf.command("repo-overview")
@click.pass_context
def conf_repo_overview(ctx):
    """Repositories overview as CSV."""
    conf = ctx.obj["config"]

    # Extract list of maintainers.
    maintainers = set()
    for repo in conf.repositories:
        maintainers.update(repo.maintainers)
    maintainers = list(sorted(maintainers))

    # Write header.
    click.echo(
        ",".join(
            [
                "Name",
                "Type," "State",
                "# Maintainers",
            ]
            + maintainers
        )
    )

    for repo in conf.repositories:
        click.echo(
            ",".join(
                [
                    repo.name,
                    repo.type,
                    repo.state,
                    str(len(repo.maintainers)),
                ]
                + _maintainer_row(maintainers, repo.maintainers)
            )
        )
