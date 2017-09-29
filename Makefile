
PROJECT:=txtrader_client
VENV:=$(HOME)/venv/$(PROJECT)
PYTHON:=python3

.PHONY: venv test install testrtx testtws clean

venv:
	@echo Building virtualenv...
	rm -rf $(VENV)
	virtualenv $(VENV) -p $(PYTHON)
	. $(VENV)/bin/activate && pip install requests simplejson pytest

TESTS := $(wildcard $(PROJECT)/*_test.py)
TPARM := -xvvs

test: $(TESTS)
	@echo "Testing..."
	. $(VENV)/bin/activate && cd $(PROJECT) && envdir ../env py.test $(TPARM) $(notdir $^)

install:
	@echo "Installing into virtualenv..."
	. $(VENV)/bin/activate && pip install .
	sudo cp scripts/* /usr/local/bin

testrtx:
	@echo "setting RTX backend"
	echo 'rtx' >env/TXTRADER_MODE
	echo $(ACCOUNT) >env/TXTRADER_API_ACCOUNT

testtws:
	@echo "setting TWS backend"
	echo 'tws' >env/TXTRADER_MODE
	echo $(ACCOUNT) >env/TXTRADER_API_ACCOUNT

.PHONY: uninstall
uninstall:
	@echo "Uninstalling from virtualenv..."
	. $(VENV)/bin/activate && pip uninstall -y $(PROJECT)

clean: uninstall
	@echo "removing txtrader_client"
	rm -rf $(VENV)
	rm $(PROJECT)/*.pyc
