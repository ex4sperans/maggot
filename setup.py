import os
import io
from setuptools import setup, find_packages


ROOT = os.path.abspath(os.path.dirname(__file__))


def load_requirements(filename):
    with open(os.path.join(ROOT, filename), "r") as f:
        return f.read().splitlines()


def load_readme():
    readme_path = os.path.join(ROOT, "README.md")
    with io.open(readme_path, encoding="utf-8") as f:
        return f"\n{f.read()}"


setup(
    name="maggot",
    version="0.2",
    packages=find_packages(),
    description=("A lightweight python library for keeping "
                 "track of numerical experiments"),
    long_description=load_readme(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "maggot=maggot.__main__:main",
        ],
    },
    include_package_data=True,
    install_requires=load_requirements("requirements.txt"),
    author="Dmytro Danevskyi",
    author_email="d.danevskyi@gmail.com"
)
