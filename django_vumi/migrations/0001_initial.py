# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-16 16:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('uid', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('enabled', models.BooleanField(default=True)),
                ('ctype', models.CharField(max_length=50)),
                ('label', models.CharField(max_length=100)),
                ('expiry_seconds', models.PositiveIntegerField(default=7200)),
                ('amqp_queue', models.CharField(max_length=50)),
                ('handler', models.CharField(choices=[('django_vumi.handler.echo', 'Echo'), ('django_vumi.handler.noop', 'No-Op'), (b'test_project.handler.reverse_echo', b'Reverse Echo')], max_length=255)),
                ('data', jsonfield.fields.JSONField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=100)),
                ('live', models.BooleanField(default=True)),
                ('expires_at', models.DateTimeField()),
                ('state', jsonfield.fields.JSONField(default={})),
                ('first_timestamp', models.DateTimeField()),
                ('last_timestamp', models.DateTimeField()),
                ('length', models.PositiveIntegerField()),
                ('channel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_vumi.Channel')),
            ],
        ),
        migrations.CreateModel(
            name='Junebug',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_url', models.URLField(unique=True)),
                ('enabled', models.BooleanField(default=True)),
                ('amqp_service', models.CharField(max_length=255)),
                ('amqp_exchange', models.CharField(default='vumi', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.CharField(max_length=50, primary_key=True, serialize=False)),
                ('state', models.CharField(choices=[('s', 'Sent'), ('a', 'ACKed'), ('e', 'Error')], max_length=1)),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('ack_timestamp', models.DateTimeField(blank=True, null=True)),
                ('from_address', models.CharField(max_length=50)),
                ('to_address', models.CharField(max_length=50)),
                ('session_event', models.CharField(choices=[('n', 'New'), ('r', 'Resume'), ('c', 'Close')], max_length=1)),
                ('content', models.TextField(blank=True, null=True)),
                ('extra', jsonfield.fields.JSONField(blank=True, null=True)),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='django_vumi.Conversation')),
            ],
        ),
        migrations.AddField(
            model_name='channel',
            name='junebug',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_vumi.Junebug'),
        ),
    ]
