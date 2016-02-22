from setuptools import setup

setup(
    name='aitertools',
    version='0-a0',
    description='Async Itertools',
    long_description=open('README.rst', 'rb').read().decode('utf-8'),
    author='Ryan Hiebert',
    author_email='ryan@ryanhiebert.com',
    url='https://github.com/ryanhiebert/aitertools',
    py_modules=['aitertools'],
    package_dir={'': 'src'},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    include_package_data=True,
)
