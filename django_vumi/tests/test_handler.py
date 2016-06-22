'''
Django-Vumi Dialogue-handler Tests
'''
from __future__ import unicode_literals

from django.test import TestCase

from django_vumi.models import Message, Dialogue
from django_vumi.util import gen_reply_message
from django_vumi.tests.helpers import generate_message
from django_vumi.handler import send_msg, echo, noop


class HandlerTestCase(TestCase):
    '''
    Tests the dialogue-handler
    '''
    fixtures = ['test_channel.json']

    def test_send_message(self):
        '''
        Tests that send_message works
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        send_msg(gen_reply_message('test', mobj, 'resume', None))

        convs = Dialogue.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_echo(self):
        '''
        Tests that echo handler replies back
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        echo(mobj)

        convs = Dialogue.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_noop(self):
        '''
        Tests that noop does nothing
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        noop(mobj)

        convs = Dialogue.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 1)
