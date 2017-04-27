.PHONY: docs

all: unittest

docs:
	cd docs && make html

unittest:
	pytest -s

clean:
	find . -name "*.pyc" -exec rm -f {} \;
