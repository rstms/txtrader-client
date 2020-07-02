# pypi deploy Makefile

PROJECT:=$(shell basename `pwd` | tr - _)

PYTHON=python3


# find all python sources (used to determine when to bump build number)
SOURCES:=$(shell find setup.py Makefile ${PROJECT} tests -name '*.py' | grep -v version.py)

# if VERSION=major or VERSION=minor specified, be sure a version bump will happen
$(if ${VERSION},$(shell touch ${PROJECT}/version.py))

help: 
	@echo "make tools|install|uninstall|test|dist|publish|release|clean"

# install python modules for development and testing
tools: 
	${PYTHON} -m pip install --upgrade setuptools wheel twine tox pytest pybump

test:
	@echo Testing...
	pytest -vvx $(TPARM)

install:
	@echo Installing ${PROJECT} locally
	${PYTHON} -m pip install --upgrade --editable .

uninstall: 
	@echo Uninstalling ${PROJECT} locally
	${PYTHON} -m pip uninstall -y ${PROJECT} 

fmt:
	find . -type f | grep .py$$ | egrep -v .git\|.tox\|.pytest_cache | xargs -n 1 yapf -i -vv

# ensure no uncommitted changes exist
gitclean: 
	$(if $(shell git status --porcelain), $(error "git status dirty, commit and push first"))

# bump version in VERSION and in python source
VERSION: gitclean ${SOURCES}
	# If VERSION=major|minor or sources have changed, bump corresponding version element
	# and commit after testing for any other uncommitted changes.
	#
	pybump bump --file VERSION --level $(if ${VERSION},${VERSION},'patch')
	@/bin/echo -e >${PROJECT}/version.py "DATE='$$(date +%Y-%m-%d)'\nTIME='$$(date +%H:%M:%S)'\nVERSION='$$(cat VERSION)'"
	@echo "Version bumped to `cat VERSION`"
	@EXPECTED_STATUS=$$(/bin/echo -e " M VERSION\n M ${PROJECT}/version.py");\
        if [ "`git status --porcelain`" != "$$EXPECTED_STATUS" ]; then \
	  echo "git state is dirty, not committing version update."; exit 1; \
	else \
	  echo "Committing version update..."; \
	  git add VERSION ${PROJECT}/version.py; \
	  git commit -m "bumped version to `cat VERSION`"; \
	  git push; \
	fi

# create distributable files
dist: VERSION 
	TOX_TESTENV_PASSENV=TXTRADER_HOST tox
	@echo building ${PROJECT}
	${PYTHON} setup.py sdist bdist_wheel

# set a git release tag and push it to github
release: dist
	@echo pushing Release ${PROJECT} v`cat VERSION` to github...
	TAG="v`cat VERSION`"; git tag -a $$TAG -m "Release $$TAG"; git push origin $$TAG

# ~/.pypirc must be defined if publishing to PyPI
publish: release
	$(if $(wildcard ~/.pypirc),,$(error publish failed; ~/.pypirc required))
	@echo publishing ${PROJECT} `cat VERSION` to PyPI...
	${PYTHON} -m twine upload dist/*

# remove all temporary files
clean:
	@echo Cleaning up...
	rm -rf build dist ./*.egg-info .pytest_cache .tox
	find . -type d -name __pycache__ | xargs rm -rf
	find . -name '*.pyc' | xargs rm -f
