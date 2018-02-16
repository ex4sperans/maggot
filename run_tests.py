#! /usr/bin/env python

import sys
import os

import pytest

# disable __pycache__ during tests
sys.dont_write_bytecode = True

# run pytest
pytest.main(["-v", "mag/", "tests/"])
