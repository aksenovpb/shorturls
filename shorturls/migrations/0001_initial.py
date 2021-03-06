# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-24 14:27
from __future__ import unicode_literals

from django.db import migrations, models
import shorturls.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Url',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.CharField(max_length=220, validators=[shorturls.validators.validate_url])),
                ('shortcode', models.CharField(blank=True, max_length=15, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
    ]
