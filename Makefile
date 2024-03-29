test:
	python setup.py test

run:
	$(MAKE) -C examples/run

format:
#	pip install -e .[dev]
	black schemalint setup.py

lint:
#	pip install -e .[dev]
	flake8 schemalint --ignore W503,E203,E501

build:
#	pip install wheel
	python setup.py bdist_wheel

upload:
#	pip install twine
	twine check dist/schemalint-$(shell cat VERSION)*
	twine upload dist/schemalint-$(shell cat VERSION)*

.PHONY: test format lint build upload
