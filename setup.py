import sys

try:
    from setuptools import setup, find_packages
except ImportError as e:
    print("Distribute is required for install:")
    print("    http://python-distribute.org/distribute_setup.py")
    sys.exit(1)

# Not supported for Python versions < 2.6
if sys.version_info <= (2, 6):
    print("Python 2.6 or greater is required.")
    sys.exit(1)

requires = [
    'flask',
    'flask-login',
    'flask-wtf',
    'sqlalchemy',
    'flask-sqlalchemy',
    'softlayer',
    'alembic',
    'pyotp',
    'pillow',
    'qrcode',
    'wtforms',
    'wtforms-parsleyjs',
]

setup(
    name='Slick',
    version='0.1',
#    description=description,
#    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=find_packages(),
    license='MIT',
#    zip_safe=False,
#    url='http://github.com/softlayer/softlayer-api-python-client',
#    entry_points={
#        'console_scripts': [
#            'sl = SoftLayer.CLI.core:main',
#        ],
#    },
#    package_data={
#        'SoftLayer': ['tests/fixtures/*'],
#    },
#    test_suite='nose.collector',
    install_requires=requires,
#    **extra
)
