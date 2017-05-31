.PHONY: docs

all: unittest

docs:
	cd docs && make html

lint:
	flake8 fuocore/

unittest: lint
	coverage run --source=fuocore setup.py test && coverage report -m

test: unittest

clean:
	find . -name "*.pyc" -exec rm -f {} \;
