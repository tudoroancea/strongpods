# Copyright (c) Tudor Oancea, 2022

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()
    # remove lines that start with #
    requirements = [
        r
        for r in requirements
        if not (r.startswith("#") or r.startswith("-e git+") or r.startswith("git+"))
    ]
    requirements_dev = fh.read().splitlines()
    # remove lines that start with #
    requirements_dev = [
        r
        for r in requirements_dev
        if not (r.startswith("#") or r.startswith("-e git+") or r.startswith("git+"))
    ]

setup(
    name="strongpods",
    version="1.0.0",
    url="",
    author="Tudor Oancea",
    license="MIT",
    description="Boilerplate code for a Python project suited to my needs",
    long_description=long_description,
    classifiers=[
        "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        # "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Private :: Do Not Upload",
    ],
    packages=find_packages(include=["strongpods"]),
    install_requires=requirements,
    extras_require={
        "dev": requirements_dev,
    },
)
