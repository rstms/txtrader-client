#!/bin/env python

import pytest

from txtrader_client import API
import time

import os
mode = os.environ.get('TXTRADER_MODE', 'rtx')


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
    print('uptime: %s' % repr(uptime))
    assert type(uptime) == str or type(uptime) == unicode


def test_version():
    api = API(mode)
    assert api.version()


def _find_test_symbol(api):
    test_symbols = 'IBM,MSFT,AAPL,GOOG,TSLA,SPY,GE,GM,F,EBAY,ORCL,RHAT,AMZN'
    server_symbols = api.query_symbols()
    assert type(server_symbols) == list
    symbol = None
    for s in test_symbols.split(','):
        if not s in server_symbols:
            symbol = s
            break
    assert symbol, f"cannot test; please add a test symbol that is not already present in the symbol list"
    print(f"using test symbol: {symbol}")
    return symbol


def test_symbol_price():
    api = API(mode)
    symbol = _find_test_symbol(api)

    symbols = api.query_symbols()
    assert type(symbols) == list
    assert not symbol in symbols

    data = api.query_symbol(symbol)
    assert data

    ret = api.del_symbol(symbol)
    assert ret

    assert not symbol in api.query_symbols()

    ret = api.add_symbol(symbol)
    assert ret
    assert symbol in api.query_symbols()

    p = api.query_symbol(symbol)
    assert p
    assert type(p) == dict
    assert p['symbol'] == symbol

    ret = api.del_symbol(symbol)
    assert ret
    assert not symbol in api.query_symbols()


def test_query_accounts():
    #print('mode=%s' % mode)
    api = API(mode)
    accounts = api.query_accounts()
    assert type(accounts) == list
    assert accounts
    #print('accounts: %s' % repr(accounts))

    account = _verify_test_account(api)
    ret = api.set_account(account)
    assert ret

    #print('query_account(%s)...' % account)
    data = api.query_account(account)
    #print('account[%s]: %s' % (account, repr(data)))
    assert data
    assert type(data) == dict

    assert mode in ['tws', 'rtx'], 'unknown mode: %s' % mode
    if mode.lower() == 'tws':
        field = 'LiquidationValue'
    elif mode.lower() == 'rtx':
        field = 'CASH_BALANCE'

    sdata = api.query_account(account, field)
    assert sdata
    assert type(sdata) == dict
    assert set(sdata.keys()) == set([field])
    #print('account[%s]: %s' % (account, repr(sdata)))

    with pytest.raises(TypeError):
        sdata = api.query_account(account, {'invalid': True})


def _wait_for_fill(api, oid, return_on_error=False):
    print('waiting for fill...')
    done = False
    last_status = ''
    while not done:
        o = api.query_order(oid)
        if last_status != o['status']:
            last_status = o['status']
            print('order status: %s' % o['status'])
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
        p = pos[account]
        assert type(p) == dict
    else:
        p = {}
    return p


def _print_order(o, prefix=None):
    print('%s%s %s' % (prefix + ' ' if prefix else '', o['permid'], o['text']))


def _market_order(api, account, route, symbol, quantity, return_on_error=False):
    o = api.market_order(account, route, symbol, quantity)
    assert o
    _print_order(o, 'market_order(%s,%s)' % (symbol, quantity))
    assert 'permid' in o.keys()
    assert 'status' in o.keys()
    oid = o['permid']
    assert type(oid) == str
    _wait_for_fill(api, oid, return_on_error)
    return oid


def _verify_test_account(api):
    test_account = api.query_accounts()[0]
    assert ('DEMO.' in test_account) or ('TEST.' in test_account)
    return test_account


def test_trades():
    api = API(mode)
    account = _verify_test_account(api)
    route = 'DEMOEUR'

    oid = _market_order(api, account, route, 'AAPL', 1)

    p = _position(api, account)
    if 'AAPL' in p.keys() and p['AAPL'] != 0:
        oid = _market_order(api, account, route, 'AAPL', -1 * p['AAPL'])
        ostat = api.query_order(oid)
        assert ostat
        assert type(ostat) == dict
        assert 'permid' in ostat.keys()

    p = _position(api, account)
    assert not 'AAPL' in p.keys() or p['AAPL'] == 0

    oid = _market_order(api, account, route, 'AAPL', 100)

    p = _position(api, account)
    assert p
    assert type(p) == dict
    assert 'AAPL' in p.keys()

    assert p['AAPL'] == 100

    oid = _market_order(api, account, route, 'AAPL', -10)

    p = _position(api, account)
    assert 'AAPL' in p.keys()

    assert p['AAPL'] == 90


def test_staged_trades():
    api = API(mode)
    account = _verify_test_account(api)
    route = 'DEMOEUR'

    tag = 'TEST_%s' % str(time.time())

    t = api.stage_market_order(tag, account, route, 'GOOG', 10)
    assert t
    assert type(t) == dict
    _print_order(t)
    assert 'permid' in t.keys()


def test_query_orders():
    api = API(mode)
    orders = api.query_orders()
    assert orders != None
    assert type(orders) == dict


def test_trade_and_query_orders():
    api = API(mode)
    account = _verify_test_account(api)
    route = 'DEMOEUR'
    oid = _market_order(api, account, route, 'AAPL', 1)
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
    account = _verify_test_account(api)
    route = 'DEMOEUR'
    oid = _market_order(api, account, route, 'AAPL', 1)
    oid = str(oid)
    #print('oid: %s' % oid)
    execs = api.query_executions()
    #print('execs: %s' % repr(execs))
    assert type(execs) == dict
    assert execs != None
    found = None
    for k, v in execs.items():
        #print('----------------')
        #print('k=%s' % k)
        #print('v=%s' % repr(v))
        #print('%s %s %s' % (found, v['permid'], oid))
        if str(v['ORIGINAL_ORDER_ID']) == oid:
            found = k
            break
    assert found
    assert str(execs[k]['ORIGINAL_ORDER_ID']) == oid

    o = api.query_order(oid)
    assert o
    assert oid == o['permid']
    assert 'status' in o
    assert o['status'] == 'Filled'


def test_trade_submission_error_bad_symbol():
    api = API(mode)
    account = _verify_test_account(api)
    route = 'DEMOEUR'
    o = api.market_order(account, route, 'BADSYMBOL', 100)
    assert o
    assert o['status'] == 'Error'
    #print('order: %s' % repr(o))


def test_trade_submission_error_bad_quantity():
    api = API(mode)
    account = _verify_test_account(api)
    route = 'DEMOEUR'
    o = api.market_order(account, route, 'AAPL', 0)
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


def test_bars():
    api = API(mode)

    sbar = '2017-07-06 09:30:00'
    ebar = '2017-07-06 09:40:00'

    ret = api.add_symbol('SPY')
    assert ret

    ret = api.query_bars('SPY', 1, sbar, ebar)
    assert ret
    assert type(ret) == list
    bars = ret
    assert bars
    assert type(bars) == list
    for bar in bars:
        assert type(bar) == list
        assert len(bar) == 7
        _date, _time, _open, _high, _low, _close, _volume = bar
        print('%s %s %s %s %s %s %s' % (_date, _time, _open, _high, _low, _close, _volume))


def test_cancel_order():
    api = API(mode)
    ret = api.cancel_order('000')
    assert ret


def test_global_cancel():
    api = API(mode)
    ret = api.global_cancel()
    assert ret


def disable_test_gateway_logon():
    api = API(mode)
    ret = api.gateway_logon('user', 'passwd')
    assert ret


def disable_test_gateway_logoff():
    api = API(mode)
    ret = api.gateway_logoff()
    assert ret


def test_help():
    api = API(mode)
    help = api.help()
    assert type(help) == dict
