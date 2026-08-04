# SPDX-FileCopyrightText: 2019-2023 CERN.
# SPDX-License-Identifier: MIT

"""PyPI CLI."""

import click

from ..pypi import PyPIAPI
from .main import cli


@cli.group()
@click.pass_context
def pypi(ctx):
    """Repository management for PyPI."""
    ctx.obj["client"] = PyPIAPI()


@pypi.command("latest-release")
@click.pass_context
def pypi_latest_release(ctx):
    """Get latest release."""
    conf = ctx.obj["config"]
    pypi = ctx.obj["client"]

    for repo in conf.repositories:
        data = pypi.latest_release(repo.name)
        if not data:
            click.echo("{}: ".format(repo.slug) + click.style("failed", fg="red"))
        else:
            status = pypi.development_status(data["info"]["classifiers"])
            release = data["releases"][data["info"]["version"]][0]
            click.echo(
                "{repo}: {version} ({status} - {release_date})".format(
                    repo=repo.slug,
                    version=data["info"]["version"],
                    status=status,
                    release_date=release["upload_time"][:10],
                )
            )
