.PHONY: docs

all: unittest

docs:
	cd docs && make html

unittest:
	coverage run --omit fuocore/third_party/netease/api.py --source=fuocore setup.py test && coverage report -m

test: unittest

clean:
	find . -name "*.pyc" -exec rm -f {} \;
