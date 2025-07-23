"""
Setup script for backward compatibility with older Python packaging tools.
Modern Python projects should use pyproject.toml, but setup.py is kept for compatibility.
"""

from setuptools import setup

if __name__ == "__main__":
    setup()