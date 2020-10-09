FROM python:3.6
WORKDIR /zquest

RUN apt-get update && apt-get -y install cmake

COPY Makefile Makefile
RUN make allegro

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY test_data test_data
COPY setup.py setup.py
COPY lib lib
COPY src src

RUN make cython

ENTRYPOINT ["python", "src/main.py"]
