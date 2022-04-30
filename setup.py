# ========================= #
# SETUP CLI                 #
# ========================= #

import os
from setuptools import setup, find_packages

def read(rel_path: str) -> str:
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path)) as fp:
        return fp.read()

def get_version(rel_path: str) -> str:
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    raise RuntimeError("Unable to find version string.")

# ========================= #
# MSCLI SETUP               #
# ========================= #

long_description = "Minecraft Server Command Line Interface"

setup(
    name="mscli",
	version=get_version("src/mscli/__init__.py"),
	description="Minecraft Server command line utility.",
	long_description=long_description,
	license="MIT",
	classifiers=[
		"License :: OSI Approved :: MIT License",
		"Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
	],
	url="https://github.com/pomaretta/mscli",
	author="Carlos Pomares",
	author_email="cpomaresp@gmail.com",
	include_package_data=True,
	package_dir={"": "src"},
	packages=find_packages(
		where="src",
		exclude=["test","scripts"],
	),
	scripts=[
		"bin/mscli",
		"bin/mscli.cmd",
	],
	install_requires=[
		"boto3",
		"mcstatus",
		"requests",
		"fabric",
		"cryptography==36.0.2",
		"pysftp",
	],
	python_requires=">=3.6",
)