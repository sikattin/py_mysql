# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

requires = ['mysql-connector-python']

setup(
    name='py_mysql',
    version='1.0',
    description='MySQL operation module',
    long_description=readme,
    author='Takeki Shikano',
    author_email='',
    url=None,
    license='MIT',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=requires,
    entry_points={
        'console_scripts': ['pysql=py_mysql.Scripts.execute_queries:global_entry_point'
        ],
    },
)

