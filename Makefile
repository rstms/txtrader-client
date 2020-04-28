
PROJECT:=txtrader_client
VENV:=$(HOME)/venv/$(PROJECT)
PYTHON:=python3
MODE:=rtx

# break with helpful message if a requred variable isn't set
define require_variable
$(if ${${1}},,$(error ${1} is empty))
endef 

venv:
	@echo Building virtualenv...
	rm -rf $(VENV)
	virtualenv $(VENV) -p $(PYTHON)
	. $(VENV)/bin/activate && pip install requests simplejson pytest && pip install -e .

TESTS := $(wildcard $(PROJECT)/*_test.py)
TPARM := -xvvs

install:
	@echo "Installing into virtualenv..."
	. $(VENV)/bin/activate && pip install .
	sudo cp scripts/* /usr/local/bin

uninstall:
	@echo "Uninstalling from virtualenv..."
	. $(VENV)/bin/activate && pip uninstall -y $(PROJECT)
	sudo rm -f /usr/local/bin/txtrader

test:
	@echo "Testing..."
	. $(VENV)/bin/activate && envdir env pytest $(TPARM) 

clean: 
	@echo "removing txtrader_client"
	rm -rf $(VENV) dist build
	rm -f $(PROJECT)/*.pyc
