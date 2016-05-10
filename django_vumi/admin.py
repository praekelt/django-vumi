'''
Junebug Conversation Admin
'''
from django.contrib import admin
from django_vumi.models import Junebug, Channel, Conversation, Message


# Register your models here.

class ChannelInline(admin.TabularInline):
    '''
    Channels Inline for Junebug instance
    '''
    model = Channel
    extra = 0


@admin.register(Junebug)
class JunebugAdmin(admin.ModelAdmin):
    '''
    Junebug instance Admin
    '''
    list_display = ['api_url', 'enabled']
    inlines = [ChannelInline]


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
