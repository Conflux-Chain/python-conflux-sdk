.PHONY: all build push

all: build

clean:
	rm -rf dist/

build: clean
	python3 setup.py sdist bdist_wheel

publish: 
	twine upload dist/* --repository conflux-web3

rm-doc:
	rm -rf docs/en/_build
	
gen-doc-config:
	jupyter-book config sphinx docs/en/ > docs/en/conf.py

# Note the first line relies on jupyterbook==0.11.3
doc: rm-doc gen-doc-config
	jupyter-book build docs/en/

# gen-docs:
# 	cd ./docs && \
# 	sphinx-apidoc -o ./source ../cfx_address -f -M --separate && \
# 	make html

test:
	pytest tests && export USE_TESTNET=1 && pytest tests
# cd ./docs && make doctest
