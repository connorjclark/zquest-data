# Zquest Data

This is a Python script for reading the binary data format for Zquest .qst and .zgp files.

I've only tested this on OSX.

## Installing

1. Checkout this repo.
1. `make`
1. Make sure you have installed allegro. `brew install allegro`

## Development Notes

I've only tested with a few different .qst/.zgp files. The binary formats have evolved over time, and so you may possible have a file that is not yet supported by the script. I have done some digging into the Zelda Classic repo's history to find some of those changes over time, but the repo on GitHub only goes back 4 years.

Also, I mostly made this to extract spritesheets, so I haven't yet implemented reading any of the data not related to graphics.

## Usage

`python3 src/main.py path/to/file.qst`
