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
        from django_vumi.models import DIALOGUES, DIALOGUE_HANDLERS

        # Clear list without destroying it
        for _ in range(len(DIALOGUES)):
            DIALOGUES.pop()

        handlers = DIALOGUE_HANDLERS.copy()
        handlers.update(getattr(settings, 'VUMI_HANDLERS', {}))
        for k in sorted(handlers.keys()):
            v = handlers[k]
            if resolve_object(v):
                DIALOGUES.append((v, k))
