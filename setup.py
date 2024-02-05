from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='imvis',
    version='0.0.7',
    description='Interactive visualization of 3D medical images in python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Xiangxi Meng',
    packages=find_packages(),
)