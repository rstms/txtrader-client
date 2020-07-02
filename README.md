txtrader-client
---------------

This module is a minimum dependency client for the txtrader trading api manager

## Installation
```
pip install txtrader-client
```

## Configuration
The following configuration variables are required:
```
TXTRADER_HOST
TXTRADER_USERNAME
TXTRADER_PASSWORD
TXTRADER_HTTP_PORT
TXTRADER_API_ACCOUNT
```
There are 2 ways to provide the variables:
### passed as a python dict into the constructor `API(config={'TXTRADER_HOST': 'localhost', ...})` 
### set as environment variables

## Basic Usage:
```
from txtrader_client import API

api = API()

print(api.status())

api.add_symbol('TSLA')

order = api.market_order('TSLA', 100)

print(api.query_positions())
```
