#!/usr/bin/env python
'''
Vumi AMQP message to Celery Task translator
'''
from kombu import Connection, Exchange, Queue

import django
django.setup()

from django.conf import settings  # noqa
from django_vumi.tasks import inbound, event  # noqa

QUEUE_INBOUND = '%s.inbound' % settings.JUNEBUG_AMQP['queue']
QUEUE_EVENT = '%s.event' % settings.JUNEBUG_AMQP['queue']

vumi_exchange = Exchange(
    settings.JUNEBUG_AMQP['exchange'],
    type='direct',
    durable=True,
    delivery_mode='persistent'
)
inbound_queue = Queue(QUEUE_INBOUND, exchange=vumi_exchange, routing_key=QUEUE_INBOUND)
event_queue = Queue(QUEUE_EVENT, exchange=vumi_exchange, routing_key=QUEUE_EVENT)


def process_media(body, message):
    '''
    Writes message/event as Celery tasks
    '''
    if message.delivery_info['routing_key'] == QUEUE_EVENT:
        event.delay(body)
    else:
        inbound.delay(body)

    message.ack()


with Connection(settings.JUNEBUG_AMQP['service']) as conn:
    conn.connect()
    if conn.connected:
        print('Connected to %s' % conn)
        with conn.Consumer([inbound_queue, event_queue], callbacks=[process_media]) as consumer:
            looping = True
            while looping:
                try:
                    conn.drain_events()
                except KeyboardInterrupt:
                    looping = False


print('Shutting down.')
