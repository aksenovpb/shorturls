# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-01 14:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import shorturls.validators


class Migration(migrations.Migration):

    dependencies = [
        ('shorturls', '0002_url_account'),
    ]

    operations = [
        migrations.CreateModel(
            name='Logging',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('go_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Referrer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referrer', models.CharField(blank=True, max_length=220, validators=[shorturls.validators.validate_url])),
                ('url', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shorturls.Url')),
            ],
        ),
        migrations.AddField(
            model_name='logging',
            name='referrer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shorturls.Referrer'),
        ),
    ]
