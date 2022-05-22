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

bash test.sh
```

## Usage

```
usage: main.py [-h] [--save-midis] [--save-tiles] [--save-csets] input

positional arguments:
  input

options:
  -h, --help    show this help message and exit
  --save-midis  Extracts MIDI files and saves to output folder
  --save-tiles  Extracts tilesheets as PNG for a particular cset and saves to output folder
  --save-csets  Extracts csets as GPL files (ex: for use in Aseprite) and saves to output folder
```

```sh
python3 src/main.py "test_data/1st.qst"
```
