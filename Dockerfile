FROM python:3.8-buster
label maintainer="mkrueger@rstms.net"
RUN pip install --upgrade txtrader-client
ENTRYPOINT [ "/usr/local/bin/txtrader" ]
