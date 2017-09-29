txtrader-client
---------------

This module is a minimum dependency client for the txtrader trading api manager

## Installation
```
git clone git@github.com/rstms/txtrader_client.git
cd txtrader_client
make install
```


## Basic Usage:
```
from txtrader_client import API

api = API('tws')

print(api.status())

order = api.market_order('GOOG', 100)

print(api.query_positions())

```
