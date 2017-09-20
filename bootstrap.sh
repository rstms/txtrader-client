#!/bin/sh
[ -n "$TXTRADER_CLIENT_VERSION" ] || TXTRADER_CLIENT_VERSION=master
curl --location -o- https://github.com/rstms/txtrader_client/tarball/$TXTRADER_CLIENT_VERSION | tar zxfv -
mv rstms-txtrader_client-* txtrader_client
cd txtrader_client
make venv
sudo make install
