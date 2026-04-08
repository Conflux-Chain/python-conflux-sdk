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
	rm -rf docs/zh-CN/_build
gen-doc-config:
	jupyter-book config sphinx docs/en
	jupyter-book config sphinx docs/zh-CN

gen-example-from-base:
	mmg -b mmg.yml
	cp -r docs/examples/en/* docs/en/examples/
	cp -r docs/examples/zh/* docs/zh-CN/examples/

doc: rm-doc gen-doc-config gen-example-from-base
	jupyter-book build docs/en/
	jupyter-book build docs/zh-CN/

# gen-docs:
# 	cd ./docs && \
# 	sphinx-apidoc -o ./source ../cfx_address -f -M --separate && \
# 	make html

test:
	pytest tests -vv -n 3 --dist loadscope
# && export USE_TESTNET=1 && pytest tests
# cd ./docs && make doctest
