.PHONY: docs

all: unittest

docs:
	cd docs && make html

lint:
	flake8 fuocore/

unittest:
	coverage run --source=fuocore setup.py test && coverage report -m

test: lint unittest

clean:
	find . -name "*~" -exec rm -f {} \;
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*flymake.py" -exec rm -f {} \;
	find . -name "\#*.py\#" -exec rm -f {} \;
	find . -name __pycache__ -delete
