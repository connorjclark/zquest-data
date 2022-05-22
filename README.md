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
usage: main.py [-h] [--save-midis] [--save-tiles] [--cset CSET] [--save-csets] input

positional arguments:
  input

options:
  -h, --help    show this help message and exit
  --save-midis  extracts MIDI files and saves to output folder (default: False)
  --save-tiles  extracts tilesheets as PNG for a particular cset and saves to output folder (default: False)
  --cset CSET   cset to use for --save-tiles. Set to -1 to save as raw index values (default: -1)
  --save-csets  extracts csets as GPL files (ex: for use in Aseprite) and saves to output folder (default: False)
```

```sh
python3 src/main.py "test_data/1st.qst"
```
