#!/usr/bin/env python
'''
Vumi AMQP message to Celery Task translator
'''
# TODO: redo this all :-(
from kombu import Connection, Exchange, Queue

import django
django.setup()

from django_vumi.models import Channel  # noqa
from django_vumi.tasks import inbound, event  # noqa

EXCHANGES = {}
SERVICES = {}

for channel in Channel.objects.filter(enabled=True):
    exchange = EXCHANGES.setdefault(
        channel.junebug.amqp_exchange,
        Exchange(
            channel.junebug.amqp_exchange,
            type='direct',
            durable=True,
            delivery_mode='persistent'
        )
    )
    service = SERVICES.setdefault(channel.junebug.amqp_service, [])
    service.append((exchange, '%s.inbound' % channel.amqp_queue))
    service.append((exchange, '%s.event' % channel.amqp_queue))

for k, v in SERVICES.items():
    SERVICES[k] = [Queue(key, exchange=xchange, routing_key=key) for xchange, key in set(v)]


def process_media(body, message):
    '''
    Writes message/event as Celery tasks
    '''
    if message.delivery_info['routing_key'].endswith('.event'):
        event.delay(body)
    else:
        inbound.delay(body)

    message.ack()


if len(SERVICES) != 1:
    print('Need exactly one AMQP service to listen to, not %d', len(SERVICES))
    exit(1)

service = SERVICES.keys()[0]
queues = SERVICES[service]

with Connection(service) as conn:
    conn.connect()
    if conn.connected:
        print('Connected to %s\nPress Ctrl-C to stop.' % conn)
        with conn.Consumer(queues, callbacks=[process_media]) as consumer:
            looping = True
            while looping:
                try:
                    conn.drain_events()
                except KeyboardInterrupt:
                    looping = False


print('Shutting down.')
