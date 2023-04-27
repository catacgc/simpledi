from setuptools import setup, find_packages

setup(
    name='simpledi',
    version='0.4.1',
    description='Simple dependency injection container for python',
    url='https://github.com/catacgc/simpledi',
    author='Catalin Costache',
    author_email='catacgc@gmail.com',
    packages=['simpledi'],
    package_dir={'': 'src'}
)