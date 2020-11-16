import os
from setuptools import setup, find_packages


def load_requirements(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r") as f:
        return f.read().splitlines()


setup(
    name="maggot",
    version="0.2",
    packages=find_packages(),
    description=("A lightweight python library for keeping "
                 "track of numerical experiments"),
     entry_points={
        "console_scripts": [
            "maggot=maggot.__main__:main",
        ],
    },
    install_requires=load_requirements("requirements.txt"),
    author="Dmytro Danevskyi",
    author_email="d.danevskyi@gmail.com"
)
