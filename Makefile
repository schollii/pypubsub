SPHINXBUILD ?= sphinx-build
DOCS_SRC    = docs
DOCS_BUILD  = $(DOCS_SRC)/_build/html
PYTHON      ?= python
VENVDIR     ?= .venv

.PHONY: docs clean-docs venv clean-venv add-wxpy-ubuntu init-tag bump-local push-tag

docs: venv
	$(VENVDIR)/bin/$(SPHINXBUILD) -b html $(DOCS_SRC) $(DOCS_BUILD)
	@echo "HTML built at $(DOCS_BUILD)"

clean-docs:
	rm -rf $(DOCS_SRC)/_build

venv:
	@if [ ! -d "$(VENVDIR)" ]; then $(PYTHON) -m venv $(VENVDIR); fi
	$(VENVDIR)/bin/pip install --upgrade pip setuptools wheel
	$(VENVDIR)/bin/pip install -r $(DOCS_SRC)/requirements.txt
	@echo "Venv ready at $(VENVDIR)"

clean-venv:
	rm -rf $(VENVDIR)

add-wxpy-ubuntu: venv
	$(VENVDIR)/bin/pip install --upgrade pip setuptools wheel
	$(VENVDIR)/bin/pip install --only-binary=:all: -f https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-22.04 wxPython==4.2.4
	sudo apt-get install -y libsdl2-2.0-0

# Release helpers (wrap release.py). Example:
# make init-tag TAG=v4.0.7
# make bump-local BUMP=patch
# make push-tag TAG=v4.0.7
latest-tag:
	$(PYTHON) release.py get-latest-tag

init-tag:
	$(PYTHON) release.py init-tag $(TAG)

bump-local:
	$(PYTHON) release.py bump-local $(BUMP)

push-tag:
	$(PYTHON) release.py push-tag $(TAG)

push-latest-tag:
	$(PYTHON) release.py push-tag --latest

test:
	tox

test-pkg:
	tox -e pkg
