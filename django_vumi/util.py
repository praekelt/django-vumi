'''
Some simple utils
'''
import importlib
import random
from datetime import datetime


def idgen():
    '''
    Generates standard Vumi random ID
    '''
    return ''.join([random.choice('0123456789abcdef') for _ in range(32)])


def gen_reply_message(content, reply_msg, session_event, metadata):
    '''
    Generates a Vumi message to reply back to reply_msg
    '''
    ret = {
        "message_id": idgen(),
        "message_type": "user_message",
        "message_version": "20110921",

        "timestamp": str(datetime.now()),
        "in_reply_to": reply_msg.id,
        "from_addr": reply_msg.to_alias.address,
        "to_addr": reply_msg.from_alias.address,
        "session_event": session_event,
        "content": content,

        # TODO: Find a way to cache this data
        "transport_name": reply_msg.dialogue.channel.uid,
        "transport_type": reply_msg.dialogue.channel.ctype,
        "transport_metadata": {},
    }
    if metadata:
        ret['helper_metadata'] = metadata
    return ret


def cdel(dct, key):
    '''
    Optionally delete 'key' in dict 'dct'
    '''
    try:
        del dct[key]
    except KeyError:
        pass


def is_notempty(item):
    '''
    Checks for "emptiness" of data, (not falsiness)
    '''
    if item is False:
        return True
    if item == 0:
        return True
    if item:
        return True
    return False


def strip_copy(item):
    '''
    Copies provided datastructure into a new one, excluding any "empty" nodes.
    '''
    if isinstance(item, dict):
        ret = {}
        for k, v in item.items():
            v = strip_copy(v)
            if is_notempty(v):
                ret[k] = v
        if ret:
            return ret
        return None
    if isinstance(item, list):
        ret = []  # pylint: disable=R0204
        for v in item:
            v = strip_copy(v)
            if is_notempty(v):
                ret.append(v)
        if ret:
            return ret
        return None
    if is_notempty(item):
        return item
    return None


def resolve_object(name):
    '''
    Resolves an object/module based on name. Returns None if not found.
    '''
    pos = name.rfind('.')
    try:
        return getattr(importlib.import_module(name[:pos]), name[pos+1:])
    except (ImportError, AttributeError):
        return None


def update_select(select, dct):
    # Build 'current state' dict from `select`
    cdct = {k: v for v, k in select if k}

    # Clear `select` list without destroying it
    for _ in range(len(select)):
        select.pop()

    cdct.update(dct)
    for k in sorted(cdct.keys()):
        v = cdct[k]
        if resolve_object(v):
            select.append((v, k))
