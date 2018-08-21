.PHONY: docs

all: unittest

docs:
	cd docs && make html

lint:
	flake8 fuocore/

unittest: pytest

pytest:
	# install dependencies first
	pytest -v --cov=fuocore --cov-report term-missing --doctest-module

test: lint unittest

clean:
	find . -name "*~" -exec rm -f {} \;
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*flymake.py" -exec rm -f {} \;
	find . -name "\#*.py\#" -exec rm -f {} \;
	find . -name __pycache__ -delete
