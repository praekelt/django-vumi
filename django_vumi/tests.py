'''
Junebug Conversation Tests
'''
from __future__ import unicode_literals

import random
from datetime import datetime

from django.test import TestCase

from django_vumi.models import Conversation, Message
from django_vumi.util import idgen, gen_reply_message, is_notempty, strip_copy, cdel


def randstr():
    '''
    Generates random string
    '''
    CHARSET = ' 0123456789 abcdefg hijklmnop qrstuvwxyz ABCDEFG HIJKLMNOP'\
        ' QRSTUVWXYZ _/\'"`!@ #$%^&*( )-_+= '
    return ''.join([random.choice(CHARSET) for _ in range(random.randint(0, 100))])


def generate_message(addrs, direction=None, in_reply_to=None,
                     session_event='resume', content=None, helper=None):
    '''
    Generates a sample Vumi message
    '''
    direction = direction if direction is not None else random.randint(0, 1)
    if direction:
        addr1 = addrs[0]
        addr2 = addrs[1]
    else:
        addr1 = addrs[1]
        addr2 = addrs[0]

    return {
        "transport_name": "2427d857-688d-4cee-88d9-8e0e32dfdc13",
        "from_addr": addr1,
        "timestamp": str(datetime.now()),
        "in_reply_to": in_reply_to,
        "to_addr": addr2,
        "message_id": idgen(),
        "content": content if content is not None else randstr(),
        "message_version": "20110921",
        "transport_type": "telnet",
        "helper_metadata": {},
        "transport_metadata": helper if helper else {},
        "session_event": session_event,
        "message_type": "user_message"
    }


def ack_message(msg, success):
    '''
    Generates a (n)ack event based on a provided vumi user_message
    '''
    return {
        "event_id": idgen(),
        "event_type": "ack" if success else "nack",
        "helper_metadata": {},
        "message_type": "event",
        "message_version": "20110921",
        "sent_message_id": msg['message_id'],
        "timestamp": str(datetime.now()),
        "transport_metadata": {},
        "transport_name": "2427d857-688d-4cee-88d9-8e0e32dfdc13",
        "user_message_id": msg['message_id'],
    }


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


class UtilsTestCase(TestCase):
    '''
    Tests the utility functions
    '''

    def test_idgen(self):
        '''
        Tests idgen works
        '''
        self.assertEquals(len(idgen()), 32)

    def test_is_notempty(self):
        '''
        Test that is_notempty tests for emptiness, not truthyness
        '''

        # Not Empty
        for val in [False, 'a', 1, 0, 0.0, [0], {'0': None}]:
            self.assertTrue(is_notempty(val), '%s is not empty' % repr(val))

        # Empty
        for val in [None, '', (), {}, []]:
            self.assertFalse(is_notempty(val), '%s is empty' % repr(val))

    def test_cdel(self):
        '''
        Test that cdel deletes keys from dict if key exists
        '''
        dct = {'a': 1, 'b': 2, 'c': 3}
        cdel(dct, 'b')
        self.assertEquals(sorted(dct.keys()), ['a', 'c'])

    def test_cdel_missing(self):
        '''
        Test that cdel gracefully handles deletes on non-existing keys
        '''
        dct = {'a': 1, 'c': 3}
        cdel(dct, 'b')
        self.assertEquals(sorted(dct.keys()), ['a', 'c'])

    def test_strip_copy(self):
        '''
        Tests that strip_copy recursively removes all empty objects
        '''
        val = {
            'a': False,
            'b': None,
            'c': [1, 2, None, '1', ''],
            'd': {'e': 1, 'f': None},
            'g': [],
            'h': [{}, {'i': 1}, {'j': []}],
            'k': ''
        }
        self.assertEquals(strip_copy(val), {
            'a': False,
            'c': [1, 2, '1'],
            'd': {'e': 1},
            'h': [{'i': 1}],
        })

    def test_gen_reply_message(self):
        '''
        Tests that gen_reply_message generates a valid response message
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        self.assertEquals(mobj.from_address, 'a')
        self.assertEquals(mobj.to_address, 'b')

        rmsg = gen_reply_message('text', mobj, 'resume', None)
        self.assertEquals(rmsg['from_addr'], 'b')
        self.assertEquals(rmsg['to_addr'], 'a')
        self.assertEquals(rmsg['in_reply_to'], mobj.id)
        self.assertEquals(rmsg['transport_name'], '2427d857-688d-4cee-88d9-8e0e32dfdc13')
        self.assertEquals(rmsg['transport_type'], 'telnet')
        self.assertNotIn('helper_metadata', rmsg)

    def test_gen_reply_message_metadata(self):
        '''
        Tests that gen_reply_message generates a valid response message with helper_metadata
        '''
        mobj = Message.log_message(generate_message(['a', 'b'], direction=True), Message.STATE_ACK)
        self.assertEquals(mobj.from_address, 'a')
        self.assertEquals(mobj.to_address, 'b')

        rmsg = gen_reply_message('text', mobj, 'resume', {'a': 'aha'})
        self.assertEquals(rmsg['from_addr'], 'b')
        self.assertEquals(rmsg['to_addr'], 'a')
        self.assertEquals(rmsg['in_reply_to'], mobj.id)
        self.assertEquals(rmsg['transport_name'], '2427d857-688d-4cee-88d9-8e0e32dfdc13')
        self.assertEquals(rmsg['transport_type'], 'telnet')
        self.assertIn('helper_metadata', rmsg)
        self.assertEquals(rmsg['helper_metadata'], {'a': 'aha'})
