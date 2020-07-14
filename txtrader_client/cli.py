#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
  __main__.py
  -----------

  TxTraderClient module - Expose class API as CLI

  Copyright (c) 2020 Reliance Systems Inc. <mkrueger@rstms.net>
  Licensed under the MIT license.  See LICENSE for details.

"""

import click
import json
import sys

from .client import API
from .version import VERSION as __version__
from .defaults import *


class _API(API):

    def __init__(self, mode, protocol, host, port, username, password, account, route, verbose, compress):
        if not verbose:
            sys.excepthook = lambda exctype, exc, traceback: print("{}: {}".format(exctype.__name__, exc))
        config = {
            'TXTRADER_PROTOCOL': protocol,
            'TXTRADER_HOST': host,
            'TXTRADER_HTTP_PORT': port,
            'TXTRADER_USERNAME': username,
            'TXTRADER_PASSWORD': password,
            'TXTRADER_API_ACCOUNT': account,
            'TXTRADER_ROUTE': route,
        }
        self.compress = compress
        super().__init__(mode=mode, config=config)

    def output(self, response):
        if self.compress:
            print(json.dumps(response))
        else:
            print(json.dumps(response, sort_keys=True, indent=2, separators=(',', ': ')))


@click.group()
@click.option('--protocol', default=TXTRADER_PROTOCOL, envvar='TXTRADER_PROTOCOL')
@click.option('-h', '--host', default=TXTRADER_HOST, envvar='TXTRADER_HOST')
@click.option('-p', '--port', default='50080', envvar='TXTRADER_HTTP_PORT')
@click.option('-U', '--username', default=TXTRADER_USERNAME, envvar='TXTRADER_USERNAME')
@click.option('-P', '--password', default=TXTRADER_PASSWORD, envvar='TXTRADER_PASSWORD')
@click.option(
    '-a',
    '--account',
    metavar='<trading_account>',
    type=str,
    default=TXTRADER_API_ACCOUNT,
    envvar='TXTRADER_API_ACCOUNT'
)
@click.option('-r', '--route', metavar='<order_route>', type=str, default=TXTRADER_ROUTE, envvar='TXTRADER_ROUTE')
@click.option('-m', '--mode', default=TXTRADER_MODE, envvar='TXTRADER_MODE', help='mode passed to txTrader client init')
@click.option('-v', '--verbose/--no_verbose', default=False, help='output detailed error diagnostics')
@click.option('-c', '--compress/--no_compress', default=False, help='minimize JSON output')
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx, protocol, host, port, username, password, account, route, mode, verbose, compress):
    ctx.obj = _API(mode, protocol, host, port, username, password, account, route, verbose, compress)


@cli.command('status', short_help='output current API connection status')
@click.pass_obj
def status(api):
    api.output(api.status())


@cli.command('shutdown', short_help='request server shutdown, writing MESSAGE to the log')
@click.argument('message')
@click.pass_obj
def shutdown(api, message):
    api.output(api.shutdown(message))


@cli.command('uptime', short_help='output start time and elapsed time for current server instance')
@click.pass_obj
def uptime(api):
    api.output(api.uptime())


@cli.command(
    'time', short_help='output formatted timestamp string (YYYY-MM-DD HH:MM:SS) matching latest datafeed time update'
)
@click.pass_obj
def time(api):
    api.output(api.time())


@cli.command('version', short_help='output release version of current server instance')
@click.pass_obj
def version(api):
    api.output(api.version())


@cli.command('add_symbol', short_help='Request subscription to a symbol for price updates and order entry')
@click.argument('symbol')
@click.pass_obj
def add_symbol(api, symbol):
    api.output(api.add_symbol(symbol.upper()))


@cli.command('del_symbol', short_help='Delete subscription to a symbol for price updates and order entry')
@click.argument('symbol')
@click.pass_obj
def del_symbol(api, symbol):
    api.output(api.del_symbol(symbol.upper()))


@cli.command('query_symbols', short_help='Return the list of active symbols')
@click.pass_obj
def query_symbols(api):
    api.output(api.query_symbols())


@cli.command('query_all_symbols', short_help='Return current data for all active symbols')
@click.pass_obj
def query_all_symbols(api):
    api.output(api.query_all_symbols())


@cli.command('query_symbol', short_help='Return current data for given symbol')
@click.argument('symbol')
@click.pass_obj
def query_symbol(api, symbol):
    api.output(api.query_symbol(symbol.upper()))


@cli.command('query_symbol_data', short_help='Return raw data for given symbol')
@click.argument('symbol')
@click.pass_obj
def query_symbol_data(api, symbol):
    api.output(api.query_symbol_data(symbol.upper()))


@cli.command('query_symbol_bars', short_help='Return current bar data for given symbol')
@click.argument('symbol')
@click.pass_obj
def query_symbol_bars(api, symbol):
    api.output(api.query_symbol_bars(symbol.upper()))


@cli.command('query_accounts', short_help='Return the list of trading accounts')
@click.pass_obj
def query_accounts(api):
    api.output(api.query_accounts())


@cli.command(
    'query_account', short_help='Query account data for account. fields is list of fields to select; None=all fields'
)
@click.argument('account')
@click.argument('fields', default='')
@click.pass_obj
def query_account(api, account, fields):
    api.output(api.query_account(account, fields))


@cli.command('query_positions', short_help='Return dict keyed by account containing dicts of position data fields')
@click.pass_obj
def query_positions(api):
    api.output(api.query_positions())


@cli.command('query_order', short_help='Return dict containing order/ticket status fields for given order id')
@click.argument('order_id', type=str)
@click.pass_obj
def query_order(api, order_id):
    api.output(api.query_order(order_id))


@cli.command('query_orders', short_help='Return dict containing order/ticket status fields for all orders')
@click.pass_obj
def query_orders(api):
    api.output(api.query_orders())


@cli.command(
    'query_tickets', short_help='Return dict keyed by order id containing dicts of all staged order ticket data fields'
)
@click.pass_obj
def query_tickets(api):
    api.output(api.query_tickets())


@cli.command('query_execution', short_help='Return dict containing execution report data fields for given execution id')
@click.argument('execution_id', type=str)
@click.pass_obj
def query_execution(api, execution_id):
    api.output(api.query_execution(execution_id))


@cli.command(
    'query_order_executions',
    short_help='Return dict keyed by execution id containing dicts of execution report data fields for given order_id'
)
@click.argument('order_id', type=str)
@click.pass_obj
def query_order_executions(api, order_id):
    api.output(api.query_order_executions(order_id))


@cli.command(
    'query_executions', short_help='Return dict keyed by execution id containing dicts of execution report data fields'
)
@click.pass_obj
def query_executions(api):
    api.output(api.query_executions())


@cli.command('submit', short_help='Submit an order to buy/sell/sell-short, returning dict containing new order fields')
@click.argument('action', type=click.Choice(['BUY', 'SELL', 'SELLSHORT', 'BUYTOCOVER'], case_sensitive=False))
@click.argument('quantity', type=int)
@click.argument('symbol', type=str)
@click.option('--staged', type=str, default='', help='submit as staged order with tag', metavar='<tag>')
@click.option('-s', '--stop', type=float, default=None, help='specify a stop price', metavar='<stop_price>')
@click.option('-l', '--limit', type=float, default=None, help='specify a limit price', metavar='<limit_price>')
@click.option(
    '-f', '--force/--noforce', is_flag=True, default=False, help='transmit the order without a confirmation prompt'
)
@click.pass_obj
def submit(api, account, route, action, symbol, quantity, staged, stop, limit, force):
    symbol = symbol.upper()
    if 'SELL' in action:
        quantity *= -1
    if stop and limit:
        order_type = 'stop_limit'
        _limit = f' with stop {stop} and limit {limit}'
    elif stop:
        order_type = 'stop'
        _limit = f' with stop {stop}'
    elif limit:
        order_type = 'limit'
        _limit = f' with limit {limit}'
    else:
        order_type = 'market'
        submit = api.market_order
        _limit = ''
    if not force:
        _staged = 'staged ' if staged else ''
        _ticket = f" with ticket '{staged}'" if staged else ''
        description = f'{_staged}{order_type} order to {action} {abs(quantity)} {symbol}{_limit}{_ticket} account={account} route={route}'
        click.confirm(f'Submit {description}... Confirm?', abort=True)

    if order_type == 'market':
        if staged:
            ret = api.stage_market_order(staged, account, route, symbol, quantity)
        else:
            ret = api.market_order(account, route, symbol, quantity)
    elif order_type == 'stop':
        if staged:
            ret = api.stage_stop_order(staged, account, route, symbol, stop, quantity)
        else:
            ret = api.stop_order(account, route, symbol, stop, quantity)
    elif order_type == 'limit':
        if staged:
            ret = api.stage_limit_order(staged, account, route, symbol, limit, quantity)
        else:
            ret = api.limit_order(account, route, symbol, limit, quantity)
    elif order_type == 'stop_limit':
        if staged:
            ret = api.stage_stoplimit_order(staged, account, route, symbol, stop, limit, quantity)
        else:
            ret = api.stoplimit_order(account, route, symbol, stop, limit, quantity)
    else:
        raise ValueError(f'illegal order type {order_type}')

    api.output(ret)


@cli.command('market_order', short_help='Submit a market order, returning dict containing new order fields')
@click.argument('account', type=str)
@click.argument('route', type=str)
@click.argument('symbol', type=str)
@click.argument('quantity', type=int)
@click.pass_obj
def stage_market_order(api, account, route, symbol, quantity):
    api.output(api.market_order(account, route, symbol.upper(), str(quantity)))


@cli.command(
    'stage_market_order',
    short_help=
    'Submit a staged market order (displays as staged in GUI, requiring manual aproval), returning dict containing new order fields'
)
@click.argument('tag', type=str)
@click.argument('account', type=str)
@click.argument('route', type=str)
@click.argument('symbol', type=str)
@click.argument('quantity', type=int)
@click.pass_obj
def stage_market_order(api, tag, account, route, symbol, quantity):
    api.output(api.stage_market_order(tag, account, route, symbol.upper(), str(quantity)))


@cli.command('limit_order', short_help='Submit a limit order, returning dict containing new order fields')
@click.argument('account', type=str)
@click.argument('route', type=str)
@click.argument('symbol', type=str)
@click.argument('price', type=float)
@click.argument('quantity', type=int)
@click.pass_obj
def limit_order(api, account, route, symbol, price, quantity):
    api.output(api.limit_order(account, route, symbol.upper(), str(price), str(quantity)))


@cli.command('stop_order', short_help='Submit a stop order, returning dict containing new order fields')
@click.argument('account', type=str)
@click.argument('route', type=str)
@click.argument('symbol', type=str)
@click.argument('price', type=float)
@click.argument('quantity', type=int)
@click.pass_obj
def stop_order(api, account, route, symbol, price, quantity):
    api.output(api.stop_order(account, route, symbol.upper(), str(price), str(quantity)))


@cli.command('stoplimit_order', short_help='Submit a stop-limit order, returning dict containing new order fields')
@click.argument('account', type=str)
@click.argument('route', type=str)
@click.argument('symbol', type=str)
@click.argument('stop_price', type=float)
@click.argument('limit_price', type=float)
@click.argument('quantity', type=int)
@click.pass_obj
def stoplimit_order(api, account, route, symbol, stop_price, limit_price, quantity):
    api.output(api.stoplimit_order(account, route, symbol.upper(), str(stop_price), str(limit_price), str(quantity)))


@cli.command('query_bars', short_help='Return array containing status strings and lists of bar data')
@click.argument('symbol', type=str)
@click.argument('period', type=str)
@click.argument('start', type=str)
@click.argument('end', type=str)
@click.pass_obj
def query_bars(api, symbol, period, start, end):
    api.output(api.query_bars(symbol.upper(), period, start, end))


@cli.command('cancel_order', short_help='Request cancellation of a pending order')
@click.argument('order_id', type=str)
@click.pass_obj
def cancel_order(api, order_id):
    api.output(api.cancel_order(order_id))


@cli.command('global_cancel', short_help='Request cancellation of all pending orders')
@click.pass_obj
def global_cancel(api):
    api.output(api.global_cancel())


@cli.command('get_order_route', short_help='Return current order route')
@click.pass_obj
def get_order_route(api):
    api.output(api.get_order_route())


@cli.command(
    'set_order_route',
    short_help=
    "Set order route data given route {'route_name': {parameter: value, ...} (JSON string will be parsed into a route dict)}"
)
@click.argument('route', type=str)
@click.pass_obj
def set_order_route(api, route):
    api.output(api.set_order_route(route))


@cli.command('help', short_help='output server help text')
@click.pass_obj
def help(api):
    print(f"\n{api.version()['txtrader']}\n")
    _help = api.help()
    for cmd in sorted(list(_help.keys())):
        print(_help[cmd])


if __name__ == '__main__':
    cli()
