#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  client.py
  ---------

  TxTrader Client module - Expose class API as user interface.

  Copyright (c) 2015 Reliance Systems Inc. <mkrueger@rstms.net>
  Licensed under the MIT license.  See LICENSE for details.

"""

import os
import sys
import requests
from types import *

from txtrader_client.version import VERSION 

class Config():
  def __init__(self, label):
    self.envdir = '/etc/txtrader'
    self.label = label.upper()

  def get(self, key):
    name = 'TXTRADER_%s' % key
    if not name in os.environ.keys():
      if self.is_file(name):
        return self.read_file(name)
    return os.environ[name] 

  def is_file(self, key):
    return os.path.isfile(os.path.join(self.envdir, key))

  def read_file(self, key):
    return open(os.path.join(self.envdir, key)).readline().strip()

class API():
  def __init__(self, server):
    self.server=server
    self.config = Config(server)
    self.hostname = self.config.get('HOST')
    self.username = self.config.get('USERNAME')
    self.password = self.config.get('PASSWORD')
    self.port = self.config.get('HTTP_PORT')
    self.account = self.config.get('API_ACCOUNT')
    self.url='http://%s:%s' % (self.hostname, self.port)

    self.cmdmap={
      'help': (self.help, False, ()),
      'status': (self.status, False, ()),
      'version': (self.version, False, ()),
      'shutdown': (self.shutdown, False, ()),
      'uptime': (self.uptime, False, ()),
      'query_bars': (self.query_bars, True, ('symbol', 'interval', 'start_time', 'end_time')),
      'add_symbol': (self.add_symbol, True, ('symbol',)),
      'del_symbol': (self.del_symbol, True, ('symbol',)),
      'query_symbol': (self.query_symbol, True, ('symbol',)),
      'query_symbols': (self.query_symbols, True, ()),
      'set_account': (self.set_account, False, ('account',)),
      'query_accounts': (self.query_accounts, False, ()),
      'query_account': (self.query_account, True, ('account', 'fields')),
      'query_positions': (self.query_positions, True, ()),
      'query_orders': (self.query_orders, True, ()),
      'query_order': (self.query_order, True, ('order_id',)),
      'cancel_order': (self.cancel_order, True, ('order_id',)),
      'query_executions': (self.query_executions, True, ()),
      'market_order': (self.market_order, True, ('symbol', 'quantity')),
      'stage_market_order': (self.stage_market_order, True, ('tag', 'symbol', 'quantity')),
      'execute_staged_market_order': (self.execute_staged_market_order, True, ('order_id')),
      'limit_order': (self.limit_order, True, ('symbol', 'limit_price', 'quantity')),
      'stop_order': (self.stop_order, True, ('symbol', 'stop_price', 'quantity')),
      'stoplimit_order': (self.stoplimit_order, True, ('symbol', 'stop_price', 'limit_price', 'quantity')),
      'global_cancel': (self.global_cancel, True, ()),
      'gateway_logon': (self.gateway_logon, True, ('username', 'password')),
      'gateway_logoff': (self.gateway_logoff, True, ()),
      'set_primary_exchange': (self.set_primary_exchange, True, ('symbol', 'exchange')),
    }

  def cmd(self, cmd, args):
    if cmd in self.cmdmap.keys():
      func, require_account, parms = self.cmdmap[cmd]
      if require_account:
        if not self.set_account(self.account):
      	  raise Exception('Error: set_account required')
      return func(*args)
    else:
      raise Exception('Error: unknown command: %s\n' % cmd)

  def call_txtrader_api(self, function_name, args):
    url = '%s/%s' % (self.url, function_name)
    headers = {'Content-type': 'application/json', 'Connection': 'close'}
    with requests.post(url, json=args, headers=headers, auth=(self.username, self.password)) as r:
      if r.status_code != requests.codes.ok:
        r.raise_for_status()
      ret = r.json()
    return ret
     
  def help(self, *args):
    return self.call_txtrader_api('help', {})

  def status(self, *args):
    return self.call_txtrader_api('status', {})

  def version(self, *args):
    return self.call_txtrader_api('version', {})

  def shutdown(self, *args):
    return self.call_txtrader_api('shutdown', {})
 
  def uptime(self, *args):
    return self.call_txtrader_api('uptime', {})

  def query_bars(self, *args):
    args = {
      'symbol': args[0],
      'period': args[1],
      'start': args[2],
      'end': args[3]
    }
    return self.call_txtrader_api('query_bars', args)

  def add_symbol(self, *args):
    return self.call_txtrader_api('add_symbol', {'symbol': args[0]})

  def del_symbol(self, *args):
    return self.call_txtrader_api('del_symbol', {'symbol': args[0]})

  def query_symbols(self, *args):
    return self.call_txtrader_api('query_symbols', {})

  def query_symbol(self, *args):
    return self.call_txtrader_api('query_symbol', {'symbol': args[0]})

  def query_accounts(self, *args):
    return self.call_txtrader_api('query_accounts', {})

  def query_account(self, *args):
    account = args[0]
    fields = None 
    if (len(args)>1) and args[1]:
      if type(args[1]) == str: 
        fields = args[1].split(',') 
      elif type(args[1]) == ListType:
        fields = args[1]
    args={'account': account}
    if fields:
      args['fields'] = fields
    return self.call_txtrader_api('query_account', args)

  def set_account(self, *args):
    account = args[0]
    ret = self.call_txtrader_api('set_account', {'account': account})
    if ret: 
      self.account = account
    return ret

  def query_positions(self, *args):
    return self.call_txtrader_api('query_positions', {})

  def query_orders(self, *args):
    return self.call_txtrader_api('query_orders', {})

  def query_order(self, *args):
    return self.call_txtrader_api('query_order', {'id': args[0]})

  def cancel_order(self, *args):
    return self.call_txtrader_api('cancel_order', {'id': args[0]})

  def query_executions(self, *args):
    return self.call_txtrader_api('query_executions', {})

  def market_order(self, *args):
    symbol, quantity = args[0:2]
    return self.call_txtrader_api('market_order', {'symbol': symbol, 'quantity': int(quantity)})

  def stage_market_order(self, *args):
    tag, symbol, quantity = args[0:3]
    return self.call_txtrader_api('stage_market_order', {'tag': tag, 'symbol': symbol, 'quantity': int(quantity)})

  def execute_staged_market_order(self, *args):
    return self.call_txtrader_api('execute_staged_market_order', {'id': args[0]})

  def limit_order(self, *args):
    symbol, limit_price, quantity = args[0:3]
    return self.call_txtrader_api('limit_order', {'symbol': symbol, 'limit_price': float(limit_price), 'quantity': int(quantity)})
  
  def stop_order(self, *args):
    symbol, stop_price, quantity = args[0:3]
    return self.call_txtrader_api('stop_order', {'symbol': symbol, 'stop_price': float(stop_price), 'quantity': int(quantity)})

  def stoplimit_order(self, *args):
    symbol, stop_price, limit_price, quantity = args[0:4]
    return self.call_txtrader_api('stoplimit_order', {'symbol': symbol, 'stop_price': float(stop_price), 'limit_price': float(limit_price), 'quantity': int(quantity)})

  def global_cancel(self, *args):
    return self.call_txtrader_api('global_cancel', {})

  def gateway_logon(self, *args):
    username, password = args[0:2]
    return self.call_txtrader_api('gateway_logon', {'username': username, 'password': password})

  def gateway_logoff(self, *args):
    return self.call_txtrader_api('gateway_logoff', {})

  def set_primary_exchange(self, *args):
    return self.call_txtrader_api('set_primary_exchange', {'symbol': args[0], 'exchange': args[1]})

  def create_order_ticket(self, *args):
    return self.call_txtrader_api('create_order_ticket', {})

