from os import path
from setuptools import find_packages, setup

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="tftp-pilot",
    version="0.1.0",
    author="Guillaume Giamarchi",
    author_email="guillaume.giamarchi@gmail.com",
    description=("Dynamic TFTP implementation for PXE Pilot. Based on fbtftp."),
    license="MIT",
    keywords="pxe boot netboot tftp grub",
    url="https://github.com/ggiamarchi/tftp-pilot",
    packages=find_packages(exclude=["tests"]),
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: System :: Boot",
        "Topic :: System :: Boot :: Init",
        "Topic :: System :: Installation/Setup",
        "Topic :: System :: Networking",
        "Topic :: System :: Operating System",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
    ],
    install_requires=[
        "fbtftp == 0.2",
        "requests == 2.23.0",
    ]
)
