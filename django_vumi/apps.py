'''
Django-Vumi appconfig
'''
from __future__ import unicode_literals

from django.apps import AppConfig


class DjangoVumiConfig(AppConfig):
    '''
    Django-Vumi appconfig
    '''
    name = 'django_vumi'

    def ready(self):
        from django.conf import settings
        from django_vumi.handler import resolve_object
        from django_vumi.models import CONVERSATIONS

        for k, v in getattr(settings, 'VUMI_HANDLERS', {}).items():
            if resolve_object(v):
                CONVERSATIONS.append((v, k))
