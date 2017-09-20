
PROJECT:=txtrader_client
PYTHON:=$(which python2)
VENV:=$(HOME)/venv/$(PROJECT)

.PHONY: venv
venv:
	@echo Building virtualenv...
	rm -rf $(VENV)
	virtualenv $(VENV) -p $(PYTHON)
	. $(VENV)/bin/activate && pip install requests pytest

TESTS := $(wildcard $(PROJECT)/*_test.py)
TPARAM := -xvvvs
.PHONY: test
test: $(TESTS)
	@echo "Testing..."
	. $(VENV)/bin/activate && cd $(PROJECT) && envdir ../env py.test $(TPARAM) $(notdir $^)

.PHONY: install
install:
	@echo "Installing into virtualenv..."
	. $(VENV)/bin/activate && pip install .
	cp scripts/txtrader /usr/local/bin

.PHONY: uninstall
uninstall:
	@echo "Uninstalling from virtualenv..."
	. $(VENV)/bin/activate && pip uninstall -y $(PROJECT)
