# Zquest Data

This is a Python script for reading the binary data format for Zquest .qst and .zgp files.

I've only tested this on OSX.

Requires Python 3.10 or greater.

## Features

* Save quest data as JSON
* Extract tilesets to PNGs
* Extract MIDIs

## Installing

1. Checkout this repo
1. Read "Developing" instructions

TODO: publish to package manager

## Developing

```sh
python3 -m pip install Cython Pillow numpy
python3 setup.py install
python3 -m unittest
```

## Usage

```sh
python3 src/main.py "test_data/1st.qst"
```
