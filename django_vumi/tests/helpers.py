'''
Django-Vumi test helpers
'''
from __future__ import unicode_literals

import random
from datetime import datetime

from django_vumi.util import idgen


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
