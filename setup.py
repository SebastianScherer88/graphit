from setuptools import setup, find_packages

setup(
   name='graphit',
   version='0.1.0',
   author='Sebastian Scherer @ Github:SebastianScherer88',
   author_email='scherersebastian@yahoo.de',
   packages=find_packages(),
   #scripts=['bin/script1','bin/script2'],
   #url='http://pypi.python.org/pypi/PackageName/',
   entry_points={
    'console_scripts': [
        'run_graphit = graphit.main:run_graphit',
    ],
    },
   license='LICENSE.txt',
   description='A package to help visualize your internal code dependencies of a project',
   long_description=open('README.md').read(),
   install_requires=[
       "pydantic",
       "schemdraw",
       "pandas"
   ],
)