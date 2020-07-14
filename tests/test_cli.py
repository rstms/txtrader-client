import pytest
from subprocess import check_output, CalledProcessError
import json
import re
from pprint import pprint, pformat
import time


def _cmd(cmdline):
    try:
        ret = check_output(cmdline, shell=True).decode().strip()
    except CalledProcessError as cpe:
        print(repr(cpe))
        print(f'output={cpe.output}')
        raise (cpe)
    return ret


def _find_test_symbol():
    test_symbols = 'IBM,MSFT,AAPL,GOOG,TSLA,SPY,GE,GM,F,EBAY,ORCL,RHAT,AMZN'
    out = _cmd('txtrader query_symbols')
    server_symbols = json.loads(out)
    assert type(server_symbols) == list
    symbol = None
    for s in test_symbols.split(','):
        if not s in server_symbols:
            symbol = s
            break
    assert symbol, f"cannot test; please add a test symbol that is not already present in the symbol list"
    return symbol


def test_cli_add_query_del_symbols():
    symbol = _find_test_symbol()
    out = _cmd(f'txtrader add_symbol {symbol}')
    assert out
    s = json.loads(out)
    assert type(s) == dict
    out = _cmd('txtrader query_symbols')
    s = json.loads(out)
    assert type(s) == list
    assert symbol in s
    out = _cmd(f'txtrader del_symbol {symbol}')
    assert type(out) == str
    assert out == 'true'
    s = json.loads(_cmd('txtrader query_symbols'))
    assert not symbol in out


def test_cli_query_accounts():
    out = _cmd('txtrader query_accounts')
    accounts = json.loads(out)
    assert type(accounts) == list
    assert len(accounts) > 0
    assert [type(a) == str for a in accounts]


def test_cli_query_account():
    out = _cmd('txtrader query_accounts')
    accounts = json.loads(out)
    account = accounts[0]
    out = _cmd(f'txtrader query_account {account}')
    d = json.loads(out)
    assert type(d) == dict
    assert len(d.keys()) > 0
    assert [type(k) == str for k in d.keys()]

    out = _cmd(f"txtrader query_account {account} EXCESS_EQ,NOTIONAL_AMOUNT")
    d = json.loads(out)
    assert type(d) == dict
    assert len(d.keys()) == 3
    assert 'EXCESS_EQ' in d
    assert 'NOTIONAL_AMOUNT' in d
    assert '_cash' in d


def test_cli_time():
    t = json.loads(_cmd('txtrader time'))
    assert re.match('^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2}$', t)


def test_cli_status():
    t = json.loads(_cmd('txtrader status'))
    assert t == 'Up'


def test_cli_version():
    v = json.loads(_cmd('txtrader version'))
    assert type(v) == dict
    assert set(v.keys()) == set(['txtrader', 'python', 'flags'])
    assert type(v['flags']) == dict


def test_cli_uptime():
    u = json.loads(_cmd('txtrader uptime'))
    assert type(u) == str
    assert re.match('^started \\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2} \\(elapsed \\d*:\\d*:\\d*\\.\\d*\\)$', u)


def _wait_for_fill(o):
    start = time.time()
    oid = o['permid']
    if not o['status'] in ['filled', 'error']:
        time.sleep(1)
        o = json.loads(_cmd(f"txtrader query_order {oid}"))
        assert o['permid'] == oid
        print(f"status={o['status']}")
        assert (time.time() - start) < 30, 'order timeout'
    return o


def test_cli_trading():
    p = json.loads(_cmd('txtrader query_positions'))
    assert type(p) == dict
    out = _cmd('txtrader query_accounts')
    accounts = json.loads(out)
    assert set(accounts) == set(p.keys())
    account = accounts[0]
    assert type(p[account]) == dict
    original_quantity = p[account].get('TSLA', 0)

    r = json.loads(_cmd('txtrader get_order_route'))
    assert type(r) == dict
    route = list(r.keys())[0]
    assert type(route) == str
    o = json.loads(_cmd(f'txtrader market_order {account} {route} TSLA 10'))
    assert type(o) == dict
    assert 'permid' in o
    oid = o['permid']
    print(f"order {o['permid']} {o['text']}")
    o = _wait_for_fill(o)
    print(f"order {o['permid']} {o['text']}")

    p = json.loads(_cmd('txtrader query_positions'))
    assert p[account]['TSLA'] == original_quantity + 10

    o = json.loads(_cmd(f'txtrader market_order {account} {route} TSLA -- -10'))
    print(f"order {o['permid']} {o['text']}")
    o = _wait_for_fill(o)
    print(f"order {o['permid']} {o['text']}")

    p = json.loads(_cmd('txtrader query_positions'))
    assert p[account]['TSLA'] == original_quantity


"""
  TODO: add tests for these remaining commands:
  cancel_order        Request cancellation of a pending order
  global_cancel       Request cancellation of all pending orders
  help                output server help text
  limit_order         Submit a limit order, returning dict containing new
  query_bars          Return array containing status strings and lists of bar
  query_executions    Return dict keyed by execution id containing dicts of
  query_orders        Return dict containing order/ticket status fields for
  query_symbol_bars   Return current bar data for given symbol
  query_symbol_data   Return raw data for given symbol
  query_tickets       Return dict keyed by order id containing dicts of all
  set_order_route     Set order route data given route {'route_name':
  stage_market_order  Submit a staged market order (displays as staged in GUI,
  stop_order          Submit a stop order, returning dict containing new order
  stoplimit_order     Submit a stop-limit order, returning dict containing new
"""
