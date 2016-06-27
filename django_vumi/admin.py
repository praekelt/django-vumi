'''
Junebug Dialogue Admin
'''
import yaml

from django.contrib import admin
from django.utils.html import escape, mark_safe

from django_vumi.models import Junebug, Channel, Dialogue, Message, Principal, Alias


# Register your models here.

class ChannelInline(admin.TabularInline):
    '''
    Channels Inline for Junebug instance
    '''
    model = Channel
    extra = 0
    can_delete = False


@admin.register(Junebug)
class JunebugAdmin(admin.ModelAdmin):
    '''
    Junebug instance Admin
    '''
    list_display = ['api_url', 'enabled']
    inlines = [ChannelInline]


class MessageInline(admin.TabularInline):
    '''
    Message-log Inline for Dialogue
    '''
    model = Message
    fields = ['id', 'timestamp', 'ack_timestamp', 'session_event', 'state', 'from_alias',
              'to_alias', 'content', 'extra_human']
    readonly_fields = fields
    extra = 0
    can_delete = False
    ordering = ['timestamp']
    template = 'compact_tabular_inline.html'

    def extra_human(self, obj):  # pragma: nocoverage
        if obj.extra:
            return mark_safe(
                '<pre style="margin: 0;display: inline-block;max-width: 30vw">%s</pre>'
                % escape(yaml.safe_dump(obj.extra, default_flow_style=False).strip()))
        else:
            return ''
    extra_human.short_description = 'Extra'


@admin.register(Dialogue)
class DialogueAdmin(admin.ModelAdmin):
    '''
    Dialogue log-view
    '''
    list_display = ['key', 'channel', 'first_timestamp', 'length', 'live']
    fields = ['key', 'channel', 'length', 'live', 'first_timestamp', 'last_timestamp',
              'expires_at', 'state']
    readonly_fields = fields
    inlines = [MessageInline]


class AliasInlines(admin.TabularInline):
    model = Alias
    extra = 0


@admin.register(Principal)
class PrincipalAdmin(admin.ModelAdmin):
    inlines = [AliasInlines]
