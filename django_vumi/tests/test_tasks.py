'''
Django-Vumi Celery tasks Tests
'''
from __future__ import unicode_literals

import json

from django.test import TestCase

from django_vumi.models import Message, Conversation
from django_vumi.tests.helpers import generate_message, ack_message
from django_vumi.tasks import inbound, event


class TaskTestCase(TestCase):
    '''
    Tests the Celery tasks
    '''

    fixtures = ['test_channel.json']

    def test_inbound(self):
        '''
        Tests inbound processes a message
        '''
        msg = generate_message(['a', 'b'], direction=True)
        inbound(json.dumps(msg))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_event_id_mismatch(self):
        '''
        Tests that event on bad id gets ignored
        '''
        evnt = ack_message({'message_id': '1'}, True)
        event(json.dumps(evnt))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 0)

    def test_event_ack_exist(self):
        '''
        Tests event ack
        '''
        msg = generate_message(['a', 'b'], direction=True)
        msg['message_id'] = '1'
        inbound(json.dumps(msg))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)
        msg1 = [m for m in msgs if m.id == '1'][0]
        self.assertEquals(msg1.state, 'a')
        msg2 = [m for m in msgs if m.id != '1'][0]
        self.assertEquals(msg2.state, 's')

        evnt = ack_message({'message_id': msg2.id}, True)
        event(json.dumps(evnt))

        msg3 = Message.objects.get(id=msg2.id)
        self.assertEquals(msg3.state, 'a')

    def test_event_nack_exist(self):
        '''
        Tests event nack
        '''
        msg = generate_message(['a', 'b'], direction=True)
        msg['message_id'] = '1'
        inbound(json.dumps(msg))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)
        msg1 = [m for m in msgs if m.id == '1'][0]
        self.assertEquals(msg1.state, 'a')
        msg2 = [m for m in msgs if m.id != '1'][0]
        self.assertEquals(msg2.state, 's')

        evnt = ack_message({'message_id': msg2.id}, False)
        event(json.dumps(evnt))

        msg3 = Message.objects.get(id=msg2.id)
        self.assertEquals(msg3.state, 'e')

    def test_event_unknown_state(self):
        '''
        Tests event unknown-state
        '''
        msg = generate_message(['a', 'b'], direction=True)
        msg['message_id'] = '1'
        inbound(json.dumps(msg))

        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)
        msg1 = [m for m in msgs if m.id == '1'][0]
        self.assertEquals(msg1.state, 'a')
        msg2 = [m for m in msgs if m.id != '1'][0]
        self.assertEquals(msg2.state, 's')

        evnt = ack_message({'message_id': msg2.id}, True)
        evnt['event_type'] = 'unknown'
        event(json.dumps(evnt))

        msg3 = Message.objects.get(id=msg2.id)
        self.assertEquals(msg3.state, 's')
