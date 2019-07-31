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

ENTRYPOINT ["python"]
CMD ["src/main.py", "test_data/Vintage Dreams Tileset v0.1.1.qst"]
# CMD ["src/main.py", "test_data/lost_isle.qst"]
