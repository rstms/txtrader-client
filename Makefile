
PROJECT:=txtrader_client
VENV:=$(HOME)/venv/$(PROJECT)

.PHONY: venv test install testrtx testtws

venv:
	@echo Building virtualenv...
	rm -rf $(VENV)
	virtualenv $(VENV)
	. $(VENV)/bin/activate && pip install requests pytest

TESTS := $(wildcard $(PROJECT)/*_test.py)
TPARM := 

test: $(TESTS)
	@echo "Testing..."
	. $(VENV)/bin/activate && cd $(PROJECT) && envdir ../env py.test -vvvvs $(TPARM) $(notdir $^)

install:
	@echo "Installing into virtualenv..."
	. $(VENV)/bin/activate && pip install .
	cp scripts/* /usr/local/bin

testrtx:
	@echo "setting RTX backend"
	echo 'rtx' >env/TXTRADER_MODE
	echo $(ACCOUNT) >env/TXTRADER_API_ACCOUNT

testtws:
	@echo "setting TWS backend"
	echo 'tws' >env/TXTRADER_MODE
	echo $(ACCOUNT) >env/TXTRADER_API_ACCOUNT

