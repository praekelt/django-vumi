'''
Setup for Django-Vumi
'''
from setuptools import setup

setup(
    name='django_vumi',
    version='0.1.0',
    description='Scalable and task-driven VUMI integration for Django.',
    long_description=open('README.rst', 'r').read(),
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://github.com/praekelt/django-vumi',
    packages=[
        'django_vumi',
    ],
    install_requires=[
        'django',
        'python-dateutil',
        'requests',
        'celery',
        'jsonfield',
        'django-memoize',
    ],
    include_package_data=True,
    scripts=[
        'django_vumi/celery_transport.py'
    ],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: BSD License",
        "Operating System :: POSIX",
        "Development Status :: 4 - Beta",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
    ],
    zip_safe=False,
)
