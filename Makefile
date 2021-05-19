TAG = 1.0.0

.PHONY: all build push

all: build

build:
	python3 setup.py sdist bdist_wheel

publish:
	twine upload dist/conflux-${TAG}*
