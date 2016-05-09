'''
Junebug Conversation Celery tasks
'''
import json
from celery import shared_task
from django.conf import settings
from kombu import Connection

from django_vumi.models import Message
from django_vumi.util import gen_reply_message

QUEUE_PUBLISH = '%s.outbound' % settings.JUNEBUG_AMQP['queue']


def send_msg(msg):
    '''
    Sends message to Junebug for routing & log message
    '''
    data = json.dumps(msg)
    Message.log_message(msg, Message.STATE_SENT)

    with Connection(settings.JUNEBUG_AMQP['service']) as conn:
        producer = conn.Producer(routing_key=QUEUE_PUBLISH)
        producer.publish(data)


@shared_task(ignore_result=True)
def inbound(data):
    '''
    Celery task to recieve Vumi (Junebug) message and process it.
    '''
    msg = json.loads(data)
    mobj = Message.log_message(msg, Message.STATE_ACK)
    # status, data = Block.resolve_block(mobj)
    # if data:
    #     if status:
    #         omsg = data.generate_response(mobj)  # pylint: disable=E1101
    #     else:
    #         omsg = Block.rescue_conversation(mobj, data)
    # else:
    omsg = gen_reply_message("Not yet implemented, sorry", mobj, 'resume', None)
    send_msg(omsg)


@shared_task(ignore_result=True)
def event(data):
    '''
    Celery task to recieve Vumi (Junebug) event and process it.
    '''
    msg = json.loads(data)
    Message.event_message(msg)
    if msg['event_type'] in ['ack', 'nack'] and 'user_message_id' in msg.keys():
        print('%s: %s' % (msg['event_type'], msg['user_message_id']))
    else:
        print(data)
