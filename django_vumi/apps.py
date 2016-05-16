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
        from django_vumi.models import CONVERSATIONS, CONVERSATION_HANDLERS

        # Clear list without destroying it
        for a in range(len(CONVERSATIONS)):
            CONVERSATIONS.pop()

        handlers = CONVERSATION_HANDLERS.copy()
        handlers.update(getattr(settings, 'VUMI_HANDLERS', {}))
        for k in sorted(handlers.keys()):
            v = handlers[k]
            if resolve_object(v):
                CONVERSATIONS.append((v, k))
