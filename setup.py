# encoding: utf-8

from setuptools import setup


def get_version():
    return __import__('froshki').__version__

setup_config = dict(

    name='froshki',
    version=get_version(),
    license='BSD',
    url='https://github.com/drowse314-dev-ymat/froshki',
    author='drowse314-dev-ymat',
    author_email='drowse314@gmail.com',
    description='simple and poor object data mapper library',
    long_description=open('README.rst').read(),
    keywords='form forms object data mapper schema validation',
    platforms=["any"],

    packages=['froshki', 'froshki.ext'],

)


if __name__ == '__main__':
    setup(**setup_config)
