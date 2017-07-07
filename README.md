txtrader-client
---------------

This module is a minimum dependency client for the txtrader trading api manager

basic usage:
```
from txtrader_client import API

api = API('tws')

print(api.status())

order = api.market_order('GOOG', 100)

print(api.query_positions())

```
