# Generated by Django 4.1.5 on 2023-01-30 13:27

import django.contrib.auth.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('demo', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='user',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
