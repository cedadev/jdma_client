import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='jdma_client',
    version='0.2',
    packages=['jdma_client'],
    install_requires=['requests',
                      'python_dateutil',
                      'pyOpenSSL',
                      'ndg-httpsclient',
                      'jinja2',
                      'pyasn1',
                      'python-ldap'
    ],
    include_package_data=True,
    license='BSD License',  # example license
    description='A command line client to access the joint-storage data migration app on JASMIN.',
    long_description=README,
    url='http://www.ceda.ac.uk/',
    author='Neil Massey',
    author_email='support@ceda.ac.uk',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: HTTP API',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    entry_points = {
        'console_scripts': ['jdma=jdma_client.jdma:main'],
    }
)
