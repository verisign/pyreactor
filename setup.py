from setuptools import setup, find_packages

from pyreactor import __version__

_description = 'A feedback based reactor pattern.'

setup(
    version='.'.join([str(__version__[i]) for i in range(3)]),
    name='pyreactor',
    description=_description,
    packages=find_packages('.'),
    package_data={'': ['*.default']},
    include_package_data=True,
    install_requires=[],
    # Data for PyPi.
    url="https://github.vrsn.com/EdgeopsChecks/pyreactor",
    author='Kinnar Dattani',
    author_email="kdattani@verisign.com",
    zip_safe=True,
)
