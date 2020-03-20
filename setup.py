from setuptools import setup, find_packages

dependencies = [
        'kaggle',
        'numpy',
        'scipy',
        'matplotlib']

setup(
        name="Covid-19 tracker",
        author='Joey Gracey',
        author_email='joeygracey@gmail.com',
        version="0.0.0",
        packages=find_packages(),
        install_requires=dependencies,
        license="MIT",
        long_description=open('README.md').read(),
)
