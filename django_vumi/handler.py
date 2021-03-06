'''
Django-Vumi Dialogue-handler
'''
import json

from kombu import Connection

from django_vumi.models import Message
from django_vumi.util import gen_reply_message


def send_msg(msg):
    '''
    Sends message to Junebug for routing & log message
    '''
    data = json.dumps(msg)
    mobj = Message.log_message(msg, Message.STATE_SENT)
    channel = mobj.dialogue.channel

    with Connection(channel.junebug.amqp_service) as conn:
        producer = conn.Producer(routing_key='%s.outbound' % channel.amqp_queue)
        producer.publish(data)


def echo(mobj):
    '''
    Simply replies back with the received message.
    '''
    send_msg(gen_reply_message(mobj.content, mobj, 'resume', None))


def noop(mobj):  # pylint: disable=W0613
    '''
    No action.
    '''
    pass
