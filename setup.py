from setuptools import find_namespace_packages
from setuptools import setup


setup(
    name='musictool',
    version='1.1.15',
    description='set of tools to help learning scales, modes, modulations, chord progressions, voice leading, rhythm',
    long_description_content_type="text/markdown",
    url='https://github.com/tandav/musictool',
    packages=find_namespace_packages(exclude=('static*', 'tests*')),
    install_requires=[
        'mido',
        'pipe21',
    ],
)
