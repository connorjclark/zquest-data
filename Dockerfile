FROM python:3.6
WORKDIR /zquest

RUN apt-get update && apt-get -y install cmake

RUN mkdir third_party && \
  git clone --branch 4.4.3.1 https://github.com/liballeg/allegro5.git third_party/allegro && \
	cd third_party/allegro && \
  cmake . && \
  make && \
  make install && \
  ldconfig

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test_data test_data
COPY setup.py setup.py
COPY lib lib
COPY src src

RUN python3 setup.py install

ENTRYPOINT ["python"]
CMD ["src/main.py", "test_data/lost_isle.qst"]
