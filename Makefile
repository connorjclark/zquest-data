clean:
	git clean -fXd

docker:
	docker build -t zquest-data .

cython:
	python3 setup.py install

allegro:
	mkdir -p third_party
	git clone --branch 4.4.3.1 https://github.com/liballeg/allegro5.git third_party/allegro
	# hack ...
	# sed -i 's|\*allegro_errno = EDOM|//\*allegro_errno = EDOM|g' third_party/allegro/src/file.c
	cd third_party/allegro; cmake . && make && make install && ldconfig
