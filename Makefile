CC = gcc

default:
	python3 setup.py install

clean:
	git clean -fXd

allegro4_file:
	mkdir -p third_party
	git clone --branch 4.4.3.1 git@github.com:liballeg/allegro5.git third_party/allegro
	cd third_party/allegro; cmake .
	# cd third_party/allegro; gcc -Iinclude -c src/file.c
	# cd third_party/allegro; gcc -dynamiclib -undefined suppress -flat_namespace *.o -o allegro4_file.dylib
	# cd third_party/allegro; ar rcs allegro4_file.a *.o
