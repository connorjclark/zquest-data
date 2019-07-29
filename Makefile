CC = gcc

default:
	python3 setup.py install

clean:
	git clean -fXd
