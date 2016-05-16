'''
Junebug Conversation Celery tasks
'''
import json
from celery import shared_task

from django_vumi.handler import resolve_object
from django_vumi.models import Message


@shared_task(ignore_result=True)
def inbound(data):
    '''
    Celery task to recieve Vumi (Junebug) message and process it.
    '''
    msg = json.loads(data)
    mobj = Message.log_message(msg, Message.STATE_ACK)
    fun = resolve_object(mobj.conversation.channel.handler)
    fun(mobj)


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
