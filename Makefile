.PHONY: release build check

release:
	python setup.py sdist bdist_wheel upload

build:
	python setup.py build sdist
	ls -al dist
	tar tvzf $(shell ls -1 dist/webuntis-* | tail -n1)

check:
	check-manifest
