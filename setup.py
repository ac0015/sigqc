from setuptools import setup, find_packages
from codecs import open
from os import path

'''Setup constructed with help from:
   https://github.com/pypa/sampleproject/blob/master/setup.py
'''
setup(
    name = 'sigqc',
    version = '0.1.0',
    description = "A Python library for use within the context of SigQC software",
    long_description = "A library for parsing SigQC export data files and implementing a variety of analysis methods in an effort towards creating a Python-SigQC Software interface.",
    url = "https://github.com/ac0015/sigqc",
    author = "Austin Coleman",
    author_email = "austin.coleman@signalysis.com",
    packages=find_packages(),
    include_package_data=True,
    package_data={'sigqc': ['SigQCReportTemplate.docx']},
    install_requires=['python-docx']
    )
