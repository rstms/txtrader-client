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
  import simplejson as json
  import inspect
  import sys

  old_hook = sys.excepthook 
  sys.excepthook = lambda exctype,exc,traceback : print("{}: {}".format(exctype.__name__,exc))

  # throw away the command name
  argv=sys.argv
  argv.pop(0)
  
  # process any flag arguments
  flags=[]
  while len(argv) and argv[0].startswith('-'):
    flags.append(argv.pop(0))

  if '-v' in flags:
    sys.excepthook = old_hook

  # local help
  if '--help' in flags or '-h' in flags:
    methods = {n: v for (n,v) in inspect.getmembers(API(), inspect.ismethod) if not n.startswith('_')}
    for name in sorted(list(methods.keys())):
      sig = inspect.signature(methods[name])
      print('%s%s' % (name, sig))
      print('    %s' % inspect.getdoc(methods[name]))
    sys.exit(0)


  # get the command
  command = argv.pop(0)

  # ensure the command is the name of a member function
  try:
    cmd = getattr(API(), command)
  except AttributeError as ex:
    sys.stderr.write(repr(ex)+'\n')
    sys.exit(1)

  # read and type convert the arguments
  args = {}
  sig = inspect.signature(cmd)
  for argname in sig.parameters.keys():
    annotation = sig.parameters[argname].annotation
    default = sig.parameters[argname].default
    # if there's a command line parameter for this arg 
    if len(argv):
      value = argv.pop(0)
      # use the annotation, if any to convert it, otherwise default to str
      if annotation==inspect.Parameter.empty or annotation==str:
        pass
      elif annotation==int:
        value = int(value)
      elif annotation==float:
        value = float(value)
      else:
        raise ValueError('unknown argument type: %s' % repr(annotation))
    # there's no parameter, so if there's a default, use it
    elif default!=inspect.Parameter.empty:
      value = default
    else:
      # no parameter and no default, so fail 
      raise ValueError('missing argument: %s' % argname)
     
    args[argname] = value 

  # call the command function
  ret = cmd(**args)

  if ret != None:
    if '-p' in flags:
      print(json.dumps(ret, sort_keys=True, indent=2, separators=(',', ': ')))
    else:
      print(json.dumps(ret))
