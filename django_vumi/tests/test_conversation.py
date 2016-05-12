'''
Junebug Conversation Tests
'''
from __future__ import unicode_literals

from django.test import TestCase

from django_vumi.models import Conversation, Message
from django_vumi.tests.helpers import ack_message, generate_message


class ConversationTestCase(TestCase):
    '''
    Tests conversation recording
    '''
    fixtures = ['test_channel.json']

    def test_log_message(self):
        '''
        Tests log_message
        '''
        Message.log_message(generate_message(['a', 'b']), Message.STATE_ACK)
        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 1)

    def test_log_empty_message(self):
        '''
        Tests log_message with empty payload should be None
        '''
        msg = Message.log_message(generate_message(['a', 'b'], content=""), Message.STATE_ACK)
        self.assertIsNone(msg.content)

    def test_log_message_conversation(self):
        '''
        Tests log_message maps messages between 2 parties to the same conversation
        '''
        for _ in range(10):
            Message.log_message(generate_message(['a', 'b']), Message.STATE_ACK)
        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 10)

    def test_outbound_message__in_reply_to(self):
        '''
        Tests log_message maps messages based on in_reply_to
        '''
        mobj = Message.log_message(generate_message(['a', 'b']), Message.STATE_ACK)
        Message.log_message(generate_message(['c', 'd'], in_reply_to=mobj.id), Message.STATE_ACK)
        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 1)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)

    def test_conversation_close(self):
        '''
        Tests that session_event='close' closes conversation
        '''
        Message.log_message(generate_message(['a', 'b']), Message.STATE_ACK)
        Message.log_message(generate_message(['a', 'b'], session_event='close'), Message.STATE_ACK)
        Message.log_message(generate_message(['a', 'b']), Message.STATE_ACK)
        convs = Conversation.objects.all()
        self.assertEquals(len(convs), 2)
        msgs = convs[0].messages.all()
        self.assertEquals(len(msgs), 2)
        msgs = convs[1].messages.all()
        self.assertEquals(len(msgs), 1)

    def test_message_ack(self):
        '''
        Tests event-ack records correctly on message
        '''
        msg = generate_message(['a', 'b'])
        mobj1 = Message.log_message(msg, Message.STATE_SENT)
        amsg = ack_message(msg, True)
        mobj2 = Message.event_message(amsg)

        self.assertEquals(mobj1.id, mobj2.id)
        self.assertEquals(mobj2.state, Message.STATE_ACK)
        self.assertIsNotNone(mobj2.ack_timestamp)
        self.assertNotEquals(mobj2.timestamp, mobj2.ack_timestamp)

    def test_message_nack(self):
        '''
        Tests event-nack records correctly on message
        '''
        msg = generate_message(['a', 'b'])
        mobj1 = Message.log_message(msg, Message.STATE_SENT)
        amsg = ack_message(msg, False)
        mobj2 = Message.event_message(amsg)

        self.assertEquals(mobj1.id, mobj2.id)
        self.assertEquals(mobj2.state, Message.STATE_ERR)
        self.assertIsNotNone(mobj2.ack_timestamp)
        self.assertNotEquals(mobj2.timestamp, mobj2.ack_timestamp)

    def test_event_message_empty(self):
        '''
        Tests empty/bad event_message payload
        '''
        self.assertIsNone(Message.event_message({}))

    def test_event_message_unknown(self):
        '''
        Tests event_message ignoring bad event_type
        '''
        evnt = ack_message({'message_id': '1'}, True)
        evnt['event_type'] = 'unknown'
        self.assertIsNone(Message.event_message(evnt))

    def test_event_message_missing(self):
        '''
        Tests event_message with missing message fails gracefully
        '''
        evnt = ack_message({'message_id': '1'}, True)
        self.assertIsNone(Message.event_message(evnt))
