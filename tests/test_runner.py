import pytest
import sys


def run():
    sys.exit(pytest.main(["tests/test.py", "-v"]))
