# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

"""Command line interface for MetaInvenio."""

import click
from attrdict import AttrDict

from ..config import ConfigParser


@click.group()
@click.option(
    "--config", "-c", help="Configuration file path.", type=click.File(), required=True
)
@click.option("--repository", "-r", help="Repository slug", default=None, multiple=True)
@click.option(
    "--repository-type", "-t", help="Repository type", default=None, multiple=True
)
@click.pass_context
def cli(ctx, config, repository=None, repository_type=None):
    """Management tools for Invenio modules."""
    ctx.obj = AttrDict(
        {
            "config": ConfigParser(
                config,
                repository=repository,
                repository_type=repository_type,
            )
        }
    )
