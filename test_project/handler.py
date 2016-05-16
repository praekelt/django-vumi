from django_vumi.handler import gen_reply_message, send_msg

def reverse_echo(mobj):
    send_msg(gen_reply_message(mobj.content[::-1], mobj, 'resume', None))
