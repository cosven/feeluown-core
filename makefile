.PHONY: docs

all: unittest

docs:
	cd docs && make html

unittest:
	py.test -s

clean:
	find . -name "*.pyc" -exec rm -f {} \;
