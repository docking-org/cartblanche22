from setuptools import find_packages
from distutils.core import setup

# To use a consistent encoding
from codecs import open
from os import path

# here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
# with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
#     long_description = f.read()

DEPENDENCIES_FILE = 'requirements.txt'
dependencies = [pkg for line in open(DEPENDENCIES_FILE) if not line.startswith('#')
                        for pkg in map(str.strip, line.split('#')) if pkg != '']

setup(
    name='SHOPPING-CART',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html

<<<<<<< HEAD
    version='0.20210223.2',
=======
    version='0.20210223.1',
>>>>>>> 803a6770b47475c78f795ddfe75ae525af6c7845

    description='Shopping cart v1.0',
    long_description='',

    zip_safe=False,

    # The project's main homepage.
    url='https://github.com/zula1010/molecule-shopping-cart',

    # Author details
    author='Munkhzul Khurelbaatar',
    author_email='munkhzulk@gmail.com',

    # Choose your license
    license='',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        # Pick your license as you wish (should match "license" above)
        'License :: Munkhzul Khurelbaatar',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.5',
    ],

    # What does your project relate to?
    keywords='shopping cart',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=['contrib', 'docs', 'tests*', 'venv']),

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=dependencies,

    scripts=(
        'application.py',
        'config.py',
        'setup.py',
        'requirements.txt',
        '.env',
    ),
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    include_package_data=True,
    package_data={
        'static': ['app/static/*'],
        'templates': ['app/templates/*'],
    },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    # data_files=[('my_data', ['data/data_file.txt'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    # entry_points={
    #     'console_scripts': [
    #         'sample=application.py:main',
    #     ],
    # },
)