FROM python:3.8
label maintainer="mkrueger@rstms.net"
RUN pip install txtrader-client
CMD txtrader
