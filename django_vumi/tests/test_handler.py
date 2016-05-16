'''
Django-Vumi Conversation-handler Tests
'''
from __future__ import unicode_literals

from django.test import TestCase

from django_vumi.models import CONVERSATIONS, Message, Conversation
from django.apps import apps
from django_vumi.util import idgen, gen_reply_message, is_notempty, strip_copy, cdel
from django_vumi.tests.helpers import generate_message

from django_vumi.handler import resolve_object, send_msg, echo, noop

class HandlerTestCase(TestCase):
    '''
    Tests the conversation-handler
    '''
    fixtures = ['test_channel.json']

    def test_resolve_object_valid(self):
        '''
        Tests resolve_object works
        '''
        self.assertEquals(resolve_object('django_vumi.handler.resolve_object'), resolve_object)

    def test_resolve_object_module_missing(self):
        '''
        Tests resolve_object returns none on missing module
        '''
        self.assertIsNone(resolve_object('django_vumi.missing_module.stuff'))

    def test_resolve_object_object_missing(self):
        '''
        Tests resolve_object returns none on missing object in module
        '''
        self.assertIsNone(resolve_object('django_vumi.handler.missing_object'))

    def test_resolve_object_module(self):
        '''
        Tests resolve_object returns none on missing object in module
        '''
        from django_vumi import handler
        self.assertEquals(resolve_object('django_vumi.handler'), handler)

    def test_handler_registration(self):
        '''
        Tests that settings.VUMI_HANDLERS are handled to spec.
        '''
        with self.settings(VUMI_HANDLERS = {'bad': 'django_vumi.missing_module', 'good': 'django_vumi.handler.resolve_object'}):
            apps.get_app_config('django_vumi').ready()
            convs = [b for a, b in CONVERSATIONS]
            self.assertIn('good', convs)
            self.assertNotIn('bad', convs)

    def test_send_message(self):
        '''
        Tests that send_message works
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        send_msg(gen_reply_message('test', mobj, 'resume', None))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_echo(self):
        '''
        Tests that echo handler replies back
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        echo(mobj)

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_noop(self):
        '''
        Tests that noop does nothing
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        noop(mobj)

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 1)
