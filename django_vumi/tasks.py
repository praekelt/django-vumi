'''
Junebug Dialogue Celery tasks
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
    fun = resolve_object(mobj.dialogue.channel.handler)
    fun(mobj)


@shared_task(ignore_result=True)
def event(data):
    '''
    Celery task to recieve Vumi (Junebug) event and process it.
    '''
    msg = json.loads(data)
    actioned = Message.event_message(msg)
    if not actioned:
        print("Unhandled event: %s" % data)
