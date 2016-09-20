all: unittest

unittest:
	py.test -s

clean:
	find . -name "*.pyc" -exec rm -f {} \;
