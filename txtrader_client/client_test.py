#!/bin/env python

import py.test

from txtrader_client import API
import time

def test_shutdown():
  api = API('tws')
  #skip api.shutdown()
  assert api

def test_status():
  api = API('tws')
  assert api.status() == 'Up'

def test_uptime():
  api = API('tws')
  uptime = api.uptime()
  assert uptime
  assert type(uptime) == str

def test_version():
  api = API('tws')
  assert api.version()

def test_symbol_price():
  api = API('tws')
  symbols = api.query_symbols()
  assert type(symbols)==list
  if 'AAPL' in symbols:
    ret = api.del_symbol('AAPL')
    assert ret
  symbols = api.query_symbols()
  assert type(symbols) == list
  assert 'AAPL' not in symbols
  price = api.query_symbol('AAPL')
  assert not price

  ret = api.add_symbol('AAPL')
  assert ret

  p = api.query_symbol('AAPL')
  assert p 
  assert type(p) == dict
  assert p['symbol'] == 'AAPL'


def test_accounts():
  api = API('tws')
  accounts = api.query_accounts()
  assert type(accounts) == list
  assert accounts

  a = accounts[0]
  ret = api.set_account(a)
  assert ret

  data = api.query_account(a)
  assert data
  assert type(data)==dict

  sdata = api.query_account(a, 'LiquidationValue')
  assert sdata
  assert type(sdata)==dict
  assert set(sdata.keys()) == set(['LiquidationValue'])

def _wait_for_fill(api, oid):
  print('waiting for fill...')
  done = False
  while not done:
    o = api.query_order(oid)
    print('order status: %s' % o['status'])
    if o['status'] == 'Filled':
      done = True
    else:
      time.sleep(1)

def test_trades():
  api = API('tws')

  account = api.query_accounts()[0]
  
  p = api.query_positions()[account]
  assert type(p) == dict
  
  if 'AAPL' in p.keys() and p['AAPL']!=0:
    o = api.market_order('AAPL', -1 * p['AAPL'])
    assert o
    print(o)
    oid = o['permid']
    assert type(oid) == str

    ostat = api.query_order(oid)
    assert ostat
    assert type(ostat) == dict
    assert 'permid' in ostat.keys()
  
    _wait_for_fill(api, oid)  

  p = api.query_positions()
  assert not 'AAPL' in p.keys() 

  o = api.market_order('AAPL', 100)
  assert o
  assert type(o) == dict
  assert 'permid' in o.keys()
  oid = o['permid']
  _wait_for_fill(api, oid)

  p = api.query_positions()
  assert p
  assert type(p) == dict
  assert account in p.keys()
  assert type(p[account]) == dict
  p = p[account]
 
  assert type(p) == dict
  assert 'AAPL' in p.keys()
 
  assert p['AAPL'] == 100

  o = api.market_order('AAPL',-10)
  _wait_for_fill(api, o['permid'])
  p = api.query_positions()[account]
  assert 'AAPL' in p.keys()
   
  assert p['AAPL'] == 90

  orders = api.query_orders()
  assert orders
  assert type(orders) == dict
  assert oid in orders.keys()
  assert type(orders[oid]) == dict

  execs = api.query_executions()
  assert execs
  assert type(execs) == dict

def test_trade_submission_error_bad_symbol():
  api = API('tws')
  o = api.market_order('BADSYMBOL', 100)
  assert o
  assert o['status'] == 'Error'
  print('order: %s' % repr(o))

def test_trade_submission_error_bad_quantity():
  api = API('tws')
  o = api.market_order('AAPL', 0)
  assert o
  assert o['status'] == 'Error'
  print('order: %s' % repr(o))



#TODO: test other order types

#    def json_limit_order(self, args, d):
#        """limit_order('symbol', price, quantity) => {'field':, data, ...}
#    def json_stop_order(self, args, d):
#        """stop_order('symbol', price, quantity) => {'field':, data, ...}
#    def json_stoplimit_order(self, args, d):
#        """stoplimit_order('symbol', stop_price, limit_price, quantity) => {'field':, data, ...}

def test_bars():
  print()
  api = API('tws')

  sbar = '2017-07-06 09:30'
  ebar = '2017-07-06 09:40'

  ret = api.query_bars('SPY', 1, sbar, ebar)
  assert ret 
  assert type(ret) ==  list
  assert ret[0]=='OK'
  bars = ret[1]
  assert bars
  assert type(bars) == list
  for bar in bars:
    assert type(bar) == dict
    assert 'date' in bar
    assert 'open' in bar
    assert 'high' in bar
    assert 'low' in bar
    assert 'close' in bar
    assert 'volume' in bar
    print('%s %s %s %s %s %s' % (bar['date'], bar['open'], bar['high'], bar['low'], bar['close'], bar['volume']))

def test_cancel_order():
  api = API('tws')
  ret = api.cancel_order('000')
  assert ret

def test_global_cancel():
  api = API('tws')
  ret = api.global_cancel()
  assert ret

def json_gateway_logon():
  api = API('tws')
  ret = api.gateway_logon('user', 'passwd')
  assert ret

def test_gateway_logoff():
  api = API('tws')
  ret = api.gateway_logoff()
  assert ret

def test_set_primary_exchange():
  api = API('tws')
  assert api.set_primary_exchange('MSFT','NASDAQ')
  assert api.add_symbol('MSFT')
  assert api.query_symbol('MSFT')

def test_help():
  api = API('tws')
  help = api.help()
  assert type(help) == dict
