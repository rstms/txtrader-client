#!/bin/env python

import py.test

from txtrader_client import API
import time

import os
mode = os.environ['TXTRADER_MODE']
test_account = os.environ['TXTRADER_API_ACCOUNT']

def test_shutdown():
  api = API(mode)
  #skip api.shutdown()
  assert api

def test_status():
  api = API(mode)
  assert api.status() == 'Up'

def test_uptime():
  api = API(mode)
  uptime = api.uptime()
  assert uptime
  assert type(uptime) == str

def test_version():
  api = API(mode)
  assert api.version()

def test_symbol_price():
  api = API(mode)
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


def test_query_accounts():
  #print('mode=%s' % mode)
  api = API(mode)
  accounts = api.query_accounts()
  assert type(accounts) == list
  assert accounts
  #print('accounts: %s' % repr(accounts))

  a = accounts[0]
  ret = api.set_account(a)
  assert ret

  #print('query_account(%s)...' % a)
  data = api.query_account(a)
  #print('account[%s]: %s' % (a, repr(data)))
  assert data
  assert type(data)==dict

  if mode == 'tws':
    field = 'LiquidationValue'
  elif mode == 'rtx':
    field = 'CASH_BALANCE'

  sdata = api.query_account(a, field) 
  assert sdata
  assert type(sdata)==dict
  assert set(sdata.keys()) == set([field])
  #print('account[%s]: %s' % (a, repr(sdata)))

def _wait_for_fill(api, oid, return_on_error=False):
  #print('waiting for fill...')
  done = False
  while not done:
    o = api.query_order(oid)
    #print('order status: %s' % o['status'])
    if return_on_error and o['status'] == 'Error':
        return
    assert o['status'] != 'Error'
    if o['status'] == 'Filled':
      done = True
    else:
      time.sleep(1)

def _position(api, account):
  pos = api.query_positions()
  assert type(pos) == dict
  assert account in pos.keys()
  if account in pos:
    p=pos[account]
    assert type(p) == dict
  else: 
    p={}
  return p

def _market_order(api, symbol, quantity, return_on_error=False):
  o = api.market_order(symbol, quantity)
  #print('market_order(%s,%s) returned %s' % (symbol, quantity, o))
  assert o
  assert 'permid' in o.keys()
  assert 'status' in o.keys()
  oid = o['permid']
  assert type(oid) == str
  _wait_for_fill(api, oid, return_on_error)  
  return oid

def test_trades():
  api = API(mode)
  account = api.query_accounts()[0]
  api.set_account(test_account)

  oid = _market_order(api, 'AAPL',1)

  p = _position(api, account)
  if 'AAPL' in p.keys() and p['AAPL']!=0:
    oid = _market_order(api, 'AAPL', -1 * p['AAPL'])
    ostat = api.query_order(oid)
    assert ostat
    assert type(ostat) == dict
    assert 'permid' in ostat.keys()

  p = _position(api, account)
  assert not 'AAPL' in p.keys()  or p['AAPL']==0

  oid = _market_order(api, 'AAPL', 100)

  p = _position(api, account)
  assert p
  assert type(p) == dict
  assert 'AAPL' in p.keys()
 
  assert p['AAPL'] == 100

  oid = _market_order(api, 'AAPL',-10)

  p = _position(api, account)
  assert 'AAPL' in p.keys()
   
  assert p['AAPL'] == 90

def test_query_orders():
  api = API(mode)
  orders = api.query_orders()
  assert orders != None
  assert type(orders) == dict

def test_trade_and_query_orders():
  api = API(mode)
  oid = _market_order(api, 'AAPL',1)
  orders = api.query_orders()
  assert orders != None
  assert type(orders) == dict
  assert oid in orders.keys()
  assert type(orders[oid]) == dict
  assert orders[oid]['permid'] == oid
  assert 'status' in orders[oid]

def test_query_executions():
  api = API(mode)
  execs = api.query_executions()
  assert type(execs) == dict
  assert execs != None

def test_trade_and_query_executions_and_query_order():
  api = API(mode)
  oid = _market_order(api, 'AAPL',1)
  oid = str(oid)
  #print('oid: %s' % oid)
  execs = api.query_executions()
  #print('execs: %s' % repr(execs))
  assert type(execs) == dict
  assert execs != None
  found=None
  for k,v in execs.items():
      #print('----------------')
      #print('k=%s' % k)
      #print('v=%s' % repr(v))
      #print('%s %s %s' % (found, v['permid'], oid))
      if str(v['permid']) == oid:
          found = k
          break
  assert found
  assert str(execs[k]['permid']) == oid

  o = api.query_order(oid)
  assert o
  assert oid == o['permid']
  assert 'status' in o
  assert o['status']=='Filled'

def test_trade_submission_error_bad_symbol():
  api = API(mode)
  o = api.market_order('BADSYMBOL', 100)
  assert o
  assert o['status'] == 'Error'
  #print('order: %s' % repr(o))

def test_trade_submission_error_bad_quantity():
  api = API(mode)
  o = api.market_order('AAPL', 0)
  assert o
  if o['status'] != 'Error':
    oid = o['permid']
    _wait_for_fill(api, oid, True)
    o = api.query_order(oid)
    assert o['status'] == 'Error'
  #print('order: %s' % repr(o))



#TODO: test other order types

#    def json_limit_order(self, args, d):
#        """limit_order('symbol', price, quantity) => {'field':, data, ...}
#    def json_stop_order(self, args, d):
#        """stop_order('symbol', price, quantity) => {'field':, data, ...}
#    def json_stoplimit_order(self, args, d):
#        """stoplimit_order('symbol', stop_price, limit_price, quantity) => {'field':, data, ...}

def dont_test_bars():
  api = API(mode)

  sbar = '2017-07-06 09:30:00'
  ebar = '2017-07-06 09:40:00'

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
    #print('%s %s %s %s %s %s' % (bar['date'], bar['open'], bar['high'], bar['low'], bar['close'], bar['volume']))

def test_cancel_order():
  api = API(mode)
  ret = api.cancel_order('000')
  assert ret

def test_global_cancel():
  api = API(mode)
  ret = api.global_cancel()
  assert ret

def json_gateway_logon():
  api = API(mode)
  ret = api.gateway_logon('user', 'passwd')
  assert ret

def test_gateway_logoff():
  api = API(mode)
  ret = api.gateway_logoff()
  assert ret

def test_set_primary_exchange():
  api = API(mode)
  if mode == 'rtx':
      exchange = 'NAS'
  elif mode == 'tws':
      exchange = 'NASDAQ'
  assert api.set_primary_exchange('MSFT', exchange)
  assert api.add_symbol('MSFT')
  assert api.query_symbol('MSFT')

def test_help():
  api = API(mode)
  help = api.help()
  assert type(help) == dict
