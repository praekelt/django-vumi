'''
Django-Vumi util Tests
'''
from __future__ import unicode_literals

from django.apps import apps
from django.test import TestCase

from django_vumi.models import DIALOGUES, Message
from django_vumi.util import idgen, gen_reply_message, is_notempty, strip_copy, cdel, resolve_object
from django_vumi.tests.helpers import generate_message


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

    def test_handler_registration(self):
        '''
        Tests that settings.VUMI_HANDLERS are handled to spec.
        '''
        with self.settings(VUMI_HANDLERS={'bad': 'django_vumi.missing_module',
                                          'good': 'django_vumi.util.resolve_object'}):
            apps.get_app_config('django_vumi').ready()
            convs = [b for _, b in DIALOGUES]
            self.assertIn('good', convs)
            self.assertNotIn('bad', convs)

    def test_resolve_object_valid(self):
        '''
        Tests resolve_object works
        '''
        self.assertEquals(resolve_object('django_vumi.util.resolve_object'), resolve_object)

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
