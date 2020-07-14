# pypi deploy Makefile

ORG:=rstms
PROJECT:=$(shell basename `pwd` | tr - _)

PYTHON=python3

# find all python sources (used to determine when to bump build number)
#PYTHON_SOURCES:=$(shell find setup.py ${PROJECT} tests examples -name '*.py' | grep -v version.py)
PYTHON_SOURCES:=$(shell find setup.py ${PROJECT} tests examples -name '*.py')
OTHER_SOURCES:=Makefile Dockerfile setup.py setup.cfg tox.ini README.md LICENSE .gitignore .style.yapf
SOURCES:=${PYTHON_SOURCES} ${OTHER_SOURCES}

# if VERSION=major or VERSION=minor specified, be sure a version bump will happen
$(if ${VERSION},$(shell touch ${PROJECT}/version.py))

help: 
	@echo "make tools|install|uninstall|test|dist|publish|release|clean"

# install python modules for development and testing
tools: 
	${PYTHON} -m pip install --upgrade setuptools pybump pytest tox twine wheel yapf

TPARM:=-vvx
test:
	@echo Testing...
	pytest $(TPARM)

install:
	@echo Installing ${PROJECT} locally
	${PYTHON} -m pip install --upgrade --editable .

uninstall: 
	@echo Uninstalling ${PROJECT} locally
	${PYTHON} -m pip uninstall -y ${PROJECT} 

# ensure no uncommitted changes exist
gitclean: 
	$(if $(shell git status --porcelain), $(error "git status dirty, commit and push first"))

# yapf format all changed python sources
fmt: .fmt  
.fmt: ${PYTHON_SOURCES}
	@$(foreach s,$?,yapf -i -vv ${s};) 
	@touch $@

# bump version in VERSION and in python source if source files have changed since last version bump
version: VERSION
VERSION: ${SOURCES}
	@echo Changed files: $?
	# If VERSION=major|minor or sources have changed, bump corresponding version element
	# and commit after testing for any other uncommitted changes.
	#
	@pybump bump --file VERSION --level $(if ${VERSION},${VERSION},'patch')
	@/bin/echo -e >${PROJECT}/version.py "DATE='$$(date +%Y-%m-%d)'\nTIME='$$(date +%H:%M:%S)'\nVERSION='$$(cat VERSION)'"
	@echo "Version bumped to `cat VERSION`"
	@touch $@

# test with tox if sources have changed
.PHONY: tox
tox: .tox
.tox: ${SOURCES} VERSION
	@echo Changed files: $?
	TOX_TESTENV_PASSENV="TXTRADER_HOST TXTRADER_TCP_PORT TXTRADER_USERNAME TXTRADER_PASSWORD" tox
	@touch $@

# create distributable files if sources have changed
dist: .dist
.dist:	${SOURCES} .tox
	@echo Changed files: $?
	@echo Building ${PROJECT}
	${PYTHON} setup.py sdist bdist_wheel
	@touch $@

# set a git release tag and push it to github
release: gitclean .dist 
	@echo pushing Release ${PROJECT} v`cat VERSION` to github...
	TAG="v`cat VERSION`"; git tag -a $$TAG -m "Release $$TAG"; git push origin $$TAG

LOCAL_VERSION=$(shell cat VERSION)
PYPI_VERSION=$(shell pip search txtrader|awk '/txtrader-client/{print substr($$2,2,length($$2)-2)}')

pypi: release
	$(if $(wildcard ~/.pypirc),,$(error publish failed; ~/.pypirc required))
	@if [ "${LOCAL_VERSION}" != "${PYPI_VERSION}" ]; then \
	  echo publishing ${PROJECT} `cat VERSION` to PyPI...;\
	  ${PYTHON} -m twine upload dist/*;\
	else \
	  echo ${PROJECT} ${LOCAL_VERSION} is up-to-date on PyPI;\
	fi

docker: .docker
.docker: pypi
	@echo building docker image
	docker images | awk '/^${ORG}\/${PROJECT}/{print $$3}' | xargs -r -n 1 docker rmi -f
	docker build . --tag ${ORG}/${PROJECT}:$(shell cat VERSION)
	docker build . --tag ${ORG}/${PROJECT}:latest
	@touch $@

dockerhub: .dockerhub
.dockerhub: .docker 
	$(if $(wildcard ~/.docker/config.json),,$(error docker-publish failed; ~/.docker/config.json required))
	@echo pushing images to dockerhub
	docker login
	docker push ${ORG}/${PROJECT}:$(shell cat VERSION)
	docker push ${ORG}/${PROJECT}:latest

publish: .dockerhub

# remove all temporary files
clean:
	@echo Cleaning up...
	rm -rf build dist .dist ./*.egg-info .pytest_cache .tox
	find . -type d -name __pycache__ | xargs rm -rf
	find . -name '*.pyc' | xargs rm -f
