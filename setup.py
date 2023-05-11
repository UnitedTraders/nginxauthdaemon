"""A setuptools based setup module.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nginxauthdaemon',
    version='1.0.0a3',
    description='Authentication daemon for nginx-proxied or nginx-served applications',
    long_description=long_description,
    url='https://github.com/UnitedTraders/nginxauthdaemon',
    author='Alik Kurdyukov',
    author_email='akurdyukov@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='nginx auth',
    packages=find_packages(),
    package_data = {
        '': ['static/*.*', 'templates/*.*']
    },
    install_requires=[
        'click==6.6',
        'Crowd==2.0.1',
        'Flask==1.1.1',
        'itsdangerous==0.24',
        'Jinja2==2.10.1',
        'lxml==4.9.1',
        'MarkupSafe==0.23',
        'pyasn1==0.1.9',
        'pycryptodome == 3.9.0',
        'requests>=2.24.0',
        'Werkzeug==2.2.3',
        'urllib3>=1.25.9'
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage'],
    }
)
