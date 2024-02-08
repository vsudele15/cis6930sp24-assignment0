from setuptools import setup, find_packages

setup(
	name='assignment0',
	version='1.0',
	author='Vaidehi Sudele',
	author_email='vsudele@ufl.edu',
	packages=find_packages(exclude=('tests', 'docs', 'resources')),
	setup_requires=['pytest-runner'],
	tests_require=['pytest']	
)