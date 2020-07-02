from setuptools import setup, find_packages
from glob import glob
import os.path

with open("README.md", "r") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'txtrader_client', 'version.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name="txtrader-client",
    version=about['VERSION'],
    author="Matt Krueger",
    author_email="mkrueger@rstms.net",
    description="TxTrader Securities Trading API Client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/rstms/txtrader_client/',
    keywords='trading api txtrader twisted',
    packages=find_packages(exclude=('tests', 'docs')),
    data_files=[('.', ['LICENSE', 'requirements.txt'])],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    install_requires=['requests'],
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'txtrader=txtrader_client:cli',
        ],
    },
)
