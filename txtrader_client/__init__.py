#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  __init__.py
  -----------

  txTraderClient module init

  Copyright (c) 2017 Reliance Systems Inc. <mkrueger@rstms.net>
  Licensed under the MIT license.  See LICENSE for details.

"""

from txtrader_client.client import API
from txtrader_client.__version__ import __version__
from txtrader_client.__main__ import cli

__all__ = [API, __version__, cli]
