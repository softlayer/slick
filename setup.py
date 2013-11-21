import os
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
    'psycopg2',
    'qrcode',
    'wtforms',
    'wtforms-parsleyjs',
]


def find_template_dirs():
    suffix = "*.html"
    template_dirs = []

    template_dirs.append(os.path.join('templates', suffix))

    for _, dirs, _ in os.walk("slick/templates"):
        for d in dirs:
            template_dirs.append(os.path.join('templates', d, suffix))

    for _, dirs, _ in os.walk("slick/blueprints"):
        for d in dirs:
            path = 'slick/blueprints/%s/templates' % d
            if os.path.exists(path):
                template_dirs.append(os.path.join(path, suffix))

    print template_dirs
    return template_dirs


setup(
    name='Slick',
    version='0.2',
#    description=description,
#    long_description=long_description,
    author='SoftLayer Technologies, Inc.',
    author_email='sldn@softlayer.com',
    packages=find_packages(),
    include_package_data=True,
#    package_data={'slick': find_template_dirs()},
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
