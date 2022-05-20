#!/bin/bash

python3 setup.py install
autopep8 . --in-place -r --max-line-length 100
python3 -m unittest
