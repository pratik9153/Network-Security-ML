from typing import List
from setuptools import find_packages,setup

"""
setup.py is a Python project configuration file that defines package information,
dependencies, installation instructions, and how the project is distributed.
"""


def get_requirements() -> List[str]:
    """
    Return the list of requirements from requirements.txt.
    """
    requirement_lst: List[str] = []

    try:
        with open("requirements.txt", "r") as file:
            lines = file.readlines()

            for line in lines:
                requirement = line.strip()

                # Ignore empty lines and -e .
                if requirement and requirement != "-e .":
                    requirement_lst.append(requirement)

    except FileNotFoundError:
        print("requirements.txt file not found")

    return requirement_lst

setup(
    name = "NETWORKSECURITYMLOPS",
    version="0.0.1",
    author="Pratik Choudhary",
    author_email='pratikchoudhary316@gmail.com',
    packages=find_packages(),
    install_requires=get_requirements(),
)

