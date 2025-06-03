#!/bin/bash
rm -rf build/ dist/ *.egg-info/
 python -m build
 twine upload dist/*
