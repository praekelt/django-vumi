Django Vumi
===========
**Scalable and task-driven VUMI integration for Django.**

.. image:: https://travis-ci.org/praekelt/django-vumi.svg?branch=master
    :target: https://travis-ci.org/praekelt/django-vumi

.. image:: https://coveralls.io/repos/github/praekelt/django-vumi/badge.svg?branch=master
    :target: https://coveralls.io/github/praekelt/django-vumi?branch=master

.. contents:: Contents
    :depth: 5

Installation
------------

#. Install or add ``django-vumi`` to your Python path.

#. Add ``'django_vumi'`` to your ``INSTALLED_APPS`` setting.

#. For any custom conversation engine handlers, please add a dict in your settings document specifying a name and a object:
    .. code:: python
    
       VUMI_HANDLERS = {
           'Reverse Echo': 'test_project.handler.reverse_echo',
       }

#. Ensure celery app is set up. Look at ``test_project/__init__.py`` and ``test_project/celery_app.py``


Conversation Engine
-------------------

Todo.
