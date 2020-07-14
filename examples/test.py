import os
import sys
import time
from pprint import pprint

from txtrader_client import API

# Please be careful!  Be sure you're using a test account, or you'll spend some money here.


def show_positions(api, account):
    # read all account positions
    positions = api.query_positions()

    # print the position of the selected account
    pprint(positions[account])


def order_stock(api, account, route, symbol, shares):
    # submit order to sell shares of stock
    order = api.market_order(account, route, symbol, shares)
    order_id = order['permid']

    # query the order status wait for it to be filled; printing the status of the order when it changes
    last_text = None
    while order['status'] != 'Filled':
        order = api.query_order(order_id)
        if order['text'] != last_text:
            print(f"order_id {order_id} {order['text']}")
            last_text = order['text']


if __name__ == '__main__':

    # set the test system account and the route in these environment variables, or edit them here
    account = os.environ['TXTRADER_API_ACCOUNT']
    route = os.environ['TXTRADER_ROUTE']

    if not 'DEMO' in account:
        print("The author's test account has DEMO in the name, yours may be different!")
        sys.exit()

    # make a connection
    api = API()

    # print the API connection status (this should be 'Up')
    pprint(api.status())

    order_stock(api, account, route, 'GOOG', 10)

    show_positions(api, account)

    order_stock(api, account, route, 'GOOG', -10)

    show_positions(api, account)
