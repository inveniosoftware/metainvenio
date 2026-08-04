#!/usr/bin/env sh
# SPDX-FileCopyrightText: 2017-2023 CERN.
# SPDX-License-Identifier: MIT

python -m check_manifest --ignore ".*-requirements.txt"
python -m pytest
