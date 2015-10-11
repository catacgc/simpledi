from setuptools import setup, find_packages

setup(
    name='simpledi',
    url='https://github.com/catacgc/simpledi',
    version='0.2',
    description='Simple dependency injection container for python',
    author='Catalin Costache',
    author_email='catacgc@gmail.com',
    packages=['simpledi'],
    package_dir={'': 'src'}
)