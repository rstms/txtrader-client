from setuptools import setup, find_packages
from glob import glob
from os.path import basename, splitext

with open("README.md", "r") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(os.path.join(here, 'pyeze', '__version__.py'), 'r') as f:
        exec(f.read(), about)

setup(
    name='txtrader-client',
    version=about['__version__'],
    author='Matt Krueger',
    author_email='mkrueger@rstms.net',
    description='client library for txTrader trading API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/rstms/txtrader-client',
    keywords='txTrader finance financial trading api',
    packages=find_packages(exclude=('tests','docs')),
    package_dir={'': 'src'},
    data_files=[('.',['VERSION'])],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Environment :: Console',

    ],
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    install_requires=[
        'requests',
        'click',
   ],
   entry_points={
       'console_scripts': [
           'txclient=txclient:cli',
        ],
   },
)
