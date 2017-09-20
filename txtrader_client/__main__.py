#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  __main__.py
  -----------

  TxTraderClient module - Expose class API as CLI

  Copyright (c) 2017 Reliance Systems Inc. <mkrueger@rstms.net>
  Licensed under the MIT license.  See LICENSE for details.

"""

if __name__=='__main__':
  from txtrader_client.client import API
  import json
  from sys import argv
  flags=[]
  while argv[1].startswith('-'):
    flags.append(argv[1])
    del(argv[1])
  server, command = argv[1:3]
  args = argv[3:]
  ret = API(server).cmd(command, args)
  if ret != None:
    if '-p' in flags:
      print(json.dumps(ret, sort_keys=True, indent=2, separators=(',', ': ')))
    else:
      print(json.dumps(ret))
