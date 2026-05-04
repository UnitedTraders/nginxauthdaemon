"""A setuptools based setup module.
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nginxauthdaemon',
    version='1.0.0a4',
    description='Authentication daemon for nginx-proxied or nginx-served applications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/UnitedTraders/nginxauthdaemon',
    author='Alik Kurdyukov',
    author_email='akurdyukov@gmail.com',
    license='MIT',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.9',
    keywords='nginx auth',
    packages=find_packages(),
    package_data = {
        '': ['static/*.*', 'templates/*.*']
    },
    install_requires=[
        'Flask>=3.0,<4.0',
        'Crowd>=3.0,<4.0',
        'pycryptodome>=3.19,<4.0',
        'PyJWT>=2.4,<3.0',
        'requests>=2.28',
    ],
    extras_require={
        'dev': ['check-manifest'],
        'test': ['pytest', 'pytest-cov', 'freezegun'],
    }
)
