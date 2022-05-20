#!/bin/bash

python3 setup.py install
autopep8 . --in-place -r
python3 -m unittest
