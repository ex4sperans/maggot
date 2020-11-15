from setuptools import setup, find_packages

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
    author="Dmytro Danevskyi",
    author_email="d.danevskyi@gmail.com"
)
