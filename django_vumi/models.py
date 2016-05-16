'''
Django-Vumi conversation models
'''
from __future__ import unicode_literals

from datetime import timedelta

import requests
import pytz
from dateutil.parser import parse as dateparse
from django.db import models
from django.utils import timezone
from jsonfield import JSONField
from memoize import memoize

from django_vumi.util import strip_copy, cdel

# Create your models here.
CONVERSATION_HANDLERS = {
    'No-Op': 'django_vumi.handler.noop',
    'Echo': 'django_vumi.handler.echo',
}
CONVERSATIONS = [('', '')]


class Junebug(models.Model):
    '''
    Junebug instance
    '''
    api_url = models.URLField(unique=True)
    enabled = models.BooleanField(default=True)
    amqp_service = models.CharField(max_length=255)
    amqp_exchange = models.CharField(max_length=50, default='vumi')


class Channel(models.Model):
    '''
    Junebug Transports
    '''
    uid = models.CharField(max_length=50, primary_key=True)
    enabled = models.BooleanField(default=True)
    junebug = models.ForeignKey(Junebug)
    ctype = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    expiry_seconds = models.PositiveIntegerField(default=7200)
    amqp_queue = models.CharField(max_length=50)
    handler = models.CharField(max_length=255, choices=CONVERSATIONS)
    data = JSONField(null=True, blank=True)

    @classmethod
    @memoize(timeout=60)  # Memoizes common call (~10% speedup for log_message)
    def get_by_uid(cls, uid):
        '''
        Resolves channel by UID
        Fetches from Junebug if not in local db.
        '''
        obj = cls.objects.filter(uid=uid).first()
        if obj:
            return obj
        else:  # pragma: nocoverage
            for jb in Junebug.objects.filter(enabled=True):
                # Fetch channel from Junebug, and create self
                r = requests.get('%schannels/%s' % (jb.api_url, uid))
                if r.status_code == 200:
                    data = r.json()['result']
                    obj = cls(
                        uid=uid,
                        ctype=data['type'],
                        label=data.get('label', uid),
                        expiry_seconds=data.get('metadata', {}).get('expiry_seconds', 7200),
                        amqp_queue=data.get['amqp_queue']
                    )
                    cdel(data.get('metadata', {}), 'expiry_seconds')
                    for key in ['id', 'type', 'label', 'amqp_queue', 'status']:
                        cdel(data, key)
                    obj.data = strip_copy(data)
                    obj.save()
                    return obj

            # Er...
            raise Exception('Could not auto-fetch Channel')

    def __unicode__(self):  # pragma: nocoverage
        return self.label


class Conversation(models.Model):
    '''
    Junebug Conversations
    '''
    # Core properties
    channel = models.ForeignKey(Channel)
    key = models.CharField(max_length=100, db_index=True)
    live = models.BooleanField(default=True)
    expires_at = models.DateTimeField()
    state = JSONField(default={})

    # Deriveable messages
    first_timestamp = models.DateTimeField()
    last_timestamp = models.DateTimeField()
    length = models.PositiveIntegerField()

    @classmethod
    def update_or_new(cls, follow, channel, key, timestamp, finish):
        '''
        Updates or creates a conversation based on search criteria.

        follow:
            Conversation follows on this message

        or

        channel:
            Message from expected channel
        key:
            Conversation search Key
        timestamp:
            Should expire after this timestamp
        finish:
            Should we mark the conversation as finished?
        '''
        if follow:
            obj = follow.conversation
            # Force conversation to be live again - We have exact conversation to follow up on.
            obj.live = True
        else:
            obj = cls.objects.filter(
                channel=channel,
                key=key,
                live=True,
                expires_at__gte=timestamp
            ).first()
        if obj:
            obj.last_timestamp = timestamp
            obj.length += 1
        else:
            obj = cls(
                channel=channel,
                key=key,
                live=True,
                first_timestamp=timestamp,
                last_timestamp=timestamp,
                length=1
            )
        if finish:
            obj.live = False
            obj.expires_at = timezone.now()
        else:
            obj.expires_at = timezone.now() + timedelta(seconds=channel.expiry_seconds)
        obj.save()
        return obj

    def __unicode__(self):  # pragma: nocoverage
        return self.key


class Message(models.Model):
    '''
    Junebug Messages
    '''
    EVENT_CHOICES = (
        ('n', 'New'),
        ('r', 'Resume'),
        ('c', 'Close'),
    )
    EVENT_MAP = {
        None: 'r',
        'new': 'n',
        'resume': 'r',
        'close': 'c',
    }
    STATE_CHOICES = (
        ('s', 'Sent'),
        ('a', 'ACKed'),
        ('e', 'Error'),
    )
    STATE_SENT = 's'
    STATE_ACK = 'a'
    STATE_ERR = 'e'

    # Core properties
    id = models.CharField(max_length=50, primary_key=True)
    state = models.CharField(max_length=1, choices=STATE_CHOICES)
    conversation = models.ForeignKey(Conversation, related_name='messages')
    timestamp = models.DateTimeField(null=True, blank=True)
    ack_timestamp = models.DateTimeField(null=True, blank=True)
    from_address = models.CharField(max_length=50)
    to_address = models.CharField(max_length=50)
    session_event = models.CharField(max_length=1, choices=EVENT_CHOICES)
    content = models.TextField(null=True, blank=True)

    # Extra data
    extra = JSONField(null=True, blank=True)

    @classmethod
    def event_message(cls, data):
        '''
        Handle message events: Marks message as (n)ACKed.

        data:
            The message in Vumi format
        '''
        if data.get('event_type') in ['ack', 'nack'] and 'user_message_id' in data.keys():
            msg = cls.objects.filter(id=data['user_message_id']).first()
            if msg:
                msg.ack_timestamp = pytz.utc.localize(dateparse(data['timestamp']))
                msg.state = cls.STATE_ACK if data['event_type'] == 'ack' else cls.STATE_ERR
                msg.save()
            return msg
        return None

    @classmethod
    def log_message(cls, data, state):
        '''
        Log message, tries to auto-resolve the channel.

        data:
            The message in Vumi format
        state:
            * STATE_ACK  Message already ACKed.
            * STATE_SENT Message is new and not ACKed.
            * STATE_ERR  Message has had a delivery error
        '''
        # timestamp
        timestamp = pytz.utc.localize(dateparse(data['timestamp']))

        # Build conversation Key
        # if data.get('group') is not None:
        #     # TODO: What is group?
        #     pass
        key = ':'.join(sorted([str(data['from_addr']), str(data['to_addr'])]))

        # Follow-up conversation
        if data.get('in_reply_to') is not None:
            follow = cls.objects.filter(id=data['in_reply_to']).first()
        else:
            follow = None

        # Conversation
        conversation = Conversation.update_or_new(
            follow,
            Channel.get_by_uid(data['transport_name']),
            key,
            timestamp,
            data['session_event'] == 'close'
        )

        msg = cls(
            id=data['message_id'],
            state=state,
            conversation=conversation,
            timestamp=timestamp,
            from_address=data['from_addr'],
            to_address=data['to_addr'],
            session_event=cls.EVENT_MAP[data['session_event']]
        )
        if state == 'a':
            msg.ack_timestamp = timestamp

        if data['content']:
            msg.content = data['content']

        # populate extra with stripped extraneous data
        # Copy all but ignored base keys
        ignored = ['from_addr', 'to_addr', 'transport_name', 'group', 'timestamp',
                   'session_event', 'message_type', 'content', 'message_version',
                   'transport_type', 'message_id', 'in_reply_to']
        extra = {k: v for k, v in data.items() if k not in ignored}
        try:
            del extra.get('helper_metadata', {})['session_event']
        except KeyError:
            pass
        msg.extra = strip_copy(extra)
        msg.save()

        return msg

    def __unicode__(self):  # pragma: nocoverage
        return "%s:%s" % (self.conversation, self.from_address)
