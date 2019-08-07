import setuptools

import transmogripy

setuptools.setup(
    name=transmogripy.__name__,
    version=transmogripy.__version__,
    author=transmogripy.__author__,
    description='tool to convert short pascal scripts to python',
    license='gpl-2.0',
    url='https://github.com/talos-gis/transmogripy',
    packages=['transmogripy'],
    python_requires='>=3.6.0',
    include_package_data=True,
    data_files=[
        ('', ['README.md', 'CHANGELOG.md', 'LICENSE']),
    ],
)
