.PHONY: all build push

all: build

clean:
	rm -rf dist/

build: clean
	python3 setup.py sdist bdist_wheel

publish: 
	twine upload dist/* --repository conflux-web3

doc:
	rm -rf examples/py
	python3 gen_py_doc.py

# gen-docs:
# 	cd ./docs && \
# 	sphinx-apidoc -o ./source ../cfx_address -f -M --separate && \
# 	make html

test:
	pytest tests && export USE_TESTNET=1 && pytest tests
# cd ./docs && make doctest
