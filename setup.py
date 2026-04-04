#!/usr/bin/env python3
"""
Setup script for LearningAcoustics package.

This allows installation via:
    pip install -e .
or
    pip install git+https://github.com/ruerue/LearningAcoustics.git
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="LearningAcoustics",
    version="0.1.0",
    author="Ruerue",
    description="A Python library for acoustic calculations and learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ruerue/LearningAcoustics",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Education",
        "Topic :: Education",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "acoustics=acoustics.cli:main",
        ],
    },
)
