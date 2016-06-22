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

    def map_handlers(self):
        from django_vumi.util import update_select
        from django.conf import settings
        from django_vumi.models import DIALOGUES, DIALOGUE_HANDLERS

        update_select(DIALOGUES, DIALOGUE_HANDLERS)
        update_select(DIALOGUES, getattr(settings, 'VUMI_HANDLERS', {}))

    def ready(self):
        self.map_handlers()
