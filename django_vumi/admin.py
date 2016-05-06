'''
Junebug Conversation Admin
'''
from django.contrib import admin
from django_vumi.models import Channel, Conversation, Message


# Register your models here.
@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    '''
    Channels Admin
    '''
    list_display = ['label', 'ctype', 'uid']


class MessageInline(admin.TabularInline):
    '''
    Message-log Inline for Conversation
    '''
    model = Message
    fields = ['id', 'timestamp', 'ack_timestamp', 'session_event', 'state', 'from_address',
              'to_address', 'content', 'extra']
    readonly_fields = fields
    extra = 0
    can_delete = False
    ordering = ['timestamp']
    template = 'compact_tabular_inline.html'


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    '''
    Conversation log-view
    '''
    list_display = ['key', 'channel', 'first_timestamp', 'length', 'live']
    fields = ['key', 'channel', 'length', 'live', 'first_timestamp', 'last_timestamp', 'expires_at']
    readonly_fields = fields
    inlines = [MessageInline]
