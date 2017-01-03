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
    url='https://github.com/verisign/pyreactor',
    download_url='https://github.com/verisign/pyreactor/archive/v1.0.tar.gz',
    author='Kinnar Dattani',
    author_email='kdattani@verisign.com',
    keywords=['reactor pattern'],
    classifiers=[],
    zip_safe=True,
)
