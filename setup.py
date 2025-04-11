from setuptools import setup, find_packages

config = {
    'name': 'Pyra',
    'version': '0.1',
    'author': 'Greta Dolcetti, Vincenzo Arceri, Caterina Urban',
    'author_email': 'greta.dolcetti@unive.it',
    'description': 'A High-level Linter for Python Data Science Applications',
    'license': 'MPL-2.0',
    'packages': find_packages('src'),
    'package_dir': {'': 'src'},
    'entry_points': {
             'console_scripts': [
                 'pyra = lyra.main:main',
                 ]
             },
    'install_requires': [
        'graphviz==0.7.1',
        'z3',
    ],
    'scripts': [],
}

setup(**config)