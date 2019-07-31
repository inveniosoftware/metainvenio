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

from ..config import ConfigParser


@click.group()
@click.option(
    '--config', '-c', help='Configuration file path.', type=click.File(),
    required=True)
@click.option('--repository', '-r', help='Repository slug', default=None,
              multiple=True)
@click.option('--repository-type', '-t', help='Repository type', default=None,
              multiple=True)
@click.pass_context
def cli(ctx, config, repository=None, repository_type=None):
    """Management tools for Invenio modules."""
    ctx.obj = AttrDict({'config': ConfigParser(
        config,
        repository=repository,
        repository_type=repository_type,
    )})
