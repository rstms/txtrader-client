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
import re

from txtrader_client.version import VERSION
import txtrader_client.defaults


class API():

    def __init__(self, mode='rtx', config={}):

        # 1st: confguration default values from module defaults
        defaults = {
            k: getattr(txtrader_client.defaults, k)
            for k in dir(txtrader_client.defaults) if not k.startswith('__')
        }
        # 2nd: any variables set in environment override defaults
        self.config = {k: os.environ.get(k, defaults[k]) for k in defaults}
        # 3rd: parameters passed in config take highest priority
        self.config.update(config)

        protocol = self._config('PROTOCOL')
        hostname = self._config('HOST')
        port = self._config('HTTP_PORT')
        self.url = f'{protocol}://{hostname}:{port}'

        self.username = self._config('USERNAME')
        self.password = self._config('PASSWORD')

        self.account = self._config('API_ACCOUNT')
        self.route = self._config('ROUTE')

    def _config(self, key):
        name = f'TXTRADER_{key}'
        try:
            ret = self.config[name]
        except KeyError as ex:
            raise ex(f'missing config value {name}')
        return ret

    def _call_txtrader_api(self, function_name, args):
        headers = {'Content-type': 'application/json', 'Connection': 'close'}
        parameters = dict(headers=headers, auth=(self.username, self.password))
        if args:
            method = requests.post
            parameters['json'] = args
        else:
            method = requests.get
        with method(f"{self.url}/{function_name}", **parameters) as r:
            if r.status_code != requests.codes.ok:
                r.raise_for_status()
            ret = r.json()
        return ret

    def help(self):
        """Return dict containing brief documentation for each server API call"""
        return self._call_txtrader_api('help', {})

    def status(self):
        """return string describing current API connection status"""
        return self._call_txtrader_api('status', {})

    def version(self):
        """Return string containing release version of current server instance"""
        return self._call_txtrader_api('version', {})

    def shutdown(self, message: str):
        """Request server shutdown; post message to logs"""
        return self._call_txtrader_api('shutdown', {'message': message})

    def uptime(self):
        """Return string showing start time and elapsed time for current server instance"""
        return self._call_txtrader_api('uptime', {})

    def time(self):
        """Return formatted timestamp string (YYYY-MM-DD HH:MM:SS) matching latest datafeed time update"""
        return self._call_txtrader_api('time', {})

    def query_symbol_bars(self, symbol: str):
        """Return array of current live bar data for given symbol"""
        return self._call_txtrader_api('query_symbol_bars', {'symbol': symbol})

    def query_bars(self, symbol, period, start, end):
        """Return array of bar data for symbol=<str> period=<minutes_as_integer|hour|day|month> start,end='YYYY-MM-DD HH:MM[:00]'"""
        if type(symbol) != str:
            raise TypeError('symbol: %s' % repr(symbol))

        if not type(period) in [int, str]:
            raise TypeError('period: %s' % repr(period))

        if type(period) == str:
            if re.match('^\\d*$', period):
                period = int(period)
            else:
                period = period[0].upper()
                if not period in ('D', 'W', 'M'):
                    raise ValueError('period: %s must match ^([Dd]|[Mm]|[Ww]).* (DAY,WEEK,MONTH)' % repr(period))

        for label, value in (('start', start), ('end', end)):
            if type(value) == str:
                if value == '.':
                    pass
                elif re.match('^-\\d*$', value):
                    pass
                elif not re.match('^\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}(:\\d{2})*$', value):
                    raise ValueError('%s: %s must match pattern YYYY-MM-DD HH:MM[:00]' % (label, repr(value)))
            elif type(value) != int:
                raise TypeError('%s: %s' % (label, repr(value)))

        args = {'symbol': symbol, 'period': period, 'start': start, 'end': end}
        return self._call_txtrader_api('query_bars', args)

    def add_symbol(self, symbol: str):
        """Request subscription to a symbol for price updates, bardata and order entry"""
        return self._call_txtrader_api('add_symbol', {'symbol': symbol})

    def del_symbol(self, symbol: str):
        """Delete subscription to a symbol for price updates and order entry"""
        return self._call_txtrader_api('del_symbol', {'symbol': symbol})

    def query_symbols(self):
        """Return the list of active symbols"""
        return self._call_txtrader_api('query_symbols', {'data': False})

    def query_all_symbols(self):
        """Return dict keyed by symbol containing current data for all active symbols"""
        return self._call_txtrader_api('query_symbols', {'data': True})

    def query_symbol(self, symbol: str):
        """Return dict containing current data for given symbol"""
        return self._call_txtrader_api('query_symbol', {'symbol': symbol})

    def query_symbol_data(self, symbol: str):
        """Return dict containing rawdata for given symbol"""
        return self._call_txtrader_api('query_symbol_data', {'symbol': symbol})

    def query_accounts(self):
        """Return array of account names"""
        return self._call_txtrader_api('query_accounts', {})

    def query_account(self, account: str, fields: str = None):
        """Query account data for account. [fields] is list of fields to select; None=all fields"""
        if fields and (type(fields) != str):
            raise TypeError('fields: %s' % repr(fields))
        args = {'account': account}
        if fields:
            args['fields'] = fields
        ret = self._call_txtrader_api('query_account', args)
        return ret

    def set_account(self, account: str):
        """Select current active trading account"""
        ret = self._call_txtrader_api('set_account', {'account': account})
        if ret:
            self.account = account
        return ret

    def query_positions(self):
        """Return dict keyed by account containing dicts of position data fields"""
        return self._call_txtrader_api('query_positions', {})

    def query_orders(self):
        """Return dict keyed by order id containing dicts of order data fields"""
        return self._call_txtrader_api('query_orders', {})

    def query_tickets(self):
        """Return dict keyed by order id containing dicts of staged order ticket data fields"""
        return self._call_txtrader_api('query_tickets', {})

    def query_order(self, order_id: str):
        """Return dict containing order/ticket status fields for given order id"""
        return self._call_txtrader_api('query_order', {'id': order_id})

    def cancel_order(self, order_id: str):
        """Request cancellation of a pending order"""
        return self._call_txtrader_api('cancel_order', {'id': order_id})

    def query_order_executions(self, order_id: str):
        """Return dict keyed by execution id containing dicts of execution report data fields for given order_id"""
        return self._call_txtrader_api('query_order_executions', {'id': order_id})

    def query_execution(self, execution_id: str):
        """Return dict containing execution report data fields for given execution id"""
        return self._call_txtrader_api('query_execution', {'id': execution_id})

    def query_executions(self):
        """Return dict keyed by execution id containing dicts of execution report data fields"""
        return self._call_txtrader_api('query_executions', {})

    def set_order_route(self, route: str):
        """Set order route data given route {'route_name': {parameter: value, ...} (JSON string will be parsed into a route dict)}"""
        return self._call_txtrader_api('set_order_route', {'route': route})

    def get_order_route(self):
        """Return current order route as a dict"""
        return self._call_txtrader_api('get_order_route', {})

    def market_order(self, account: str, route: str, symbol: str, quantity: int):
        """Submit a market order, returning dict containing new order fields"""
        return self._call_txtrader_api(
            'market_order', {
                'account': account,
                'route': route,
                'symbol': symbol,
                'quantity': quantity
            }
        )

    def stage_market_order(self, tag: str, account: str, route: str, symbol: str, quantity: int):
        """Submit a staged market order (displays as staged in GUI, requiring manual aproval), returning dict containing new order fields"""
        return self._call_txtrader_api(
            'stage_market_order', {
                'tag': tag,
                'account': account,
                'route': route,
                'symbol': symbol,
                'quantity': quantity
            }
        )

    def limit_order(self, account: str, route: str, symbol: str, limit_price: float, quantity: int):
        """Submit a limit order, returning dict containing new order fields"""
        return self._call_txtrader_api(
            'limit_order', {
                'account': account,
                'route': route,
                'symbol': symbol,
                'limit_price': float(limit_price),
                'quantity': quantity
            }
        )

    def stop_order(self, account: str, route: str, symbol: str, stop_price: float, quantity: int):
        """Submit a stop order, returning dict containing new order fields"""
        return self._call_txtrader_api(
            'stop_order', {
                'account': account,
                'route': route,
                'symbol': symbol,
                'stop_price': stop_price,
                'quantity': quantity
            }
        )

    def stoplimit_order(
        self, account: str, route: str, symbol: str, stop_price: float, limit_price: float, quantity: int
    ):
        """Submit a stop-limit order, returning dict containing new order fields"""
        return self._call_txtrader_api(
            'stoplimit_order', {
                'account': account,
                'route': route,
                'symbol': symbol,
                'stop_price': float(stop_price),
                'limit_price': float(limit_price),
                'quantity': int(quantity)
            }
        )

    def global_cancel(self):
        """Request cancellation of all pending orders"""
        return self._call_txtrader_api('global_cancel', {})
