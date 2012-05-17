from setuptools import setup, find_packages
import sys, os

version = "0.1"

setup(
    name="peg",
    version=version,
    description="PEG (Parsing Expression Grammar) parser generator",
    author="Andrey Popp",
    author_email="8mayday@gmail.com",
    license="BSD",
    py_modules=["peg"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    entry_points="""
    # -*- Entry points: -*-
    """)
