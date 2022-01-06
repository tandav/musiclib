from setuptools import find_packages
from setuptools import setup


setup(
    name='musictool',
    version='1.0.3',
    description='set of tools to help learning scales, modes, modulations, chord progressions, voice leading, rhythm',
    long_description_content_type="text/markdown",
    url='https://github.com/tandav/musictool',
    packages=['musictool', 'musictool.*'],
)
