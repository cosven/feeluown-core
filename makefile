.PHONY: docs

all: unittest

docs:
	cd docs && make html

lint:
	flake8 fuocore/

unittest:
	python3 setup.py test

pytest:
	pip3 install -r dev-requirements.txt
	pytest --cov=fuocore --doctest-module

test: lint unittest

clean:
	find . -name "*~" -exec rm -f {} \;
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*flymake.py" -exec rm -f {} \;
	find . -name "\#*.py\#" -exec rm -f {} \;
	find . -name __pycache__ -delete
