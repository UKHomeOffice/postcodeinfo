# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


def create_super_user(apps, schema_editor):
    username = os.environ.get('ADMIN_USER_USERNAME')
    email = os.environ.get('ADMIN_USER_EMAIL')
    password = os.environ.get('ADMIN_USER_PASSWORD')

    existing_users = User.objects.filter(username=username)

    if username is None:
        print (
            'skipping admin user creation - '
            'no defaults set (ADMIN_USER_xyz)'
            )
    else:
        if existing_users:
            print (
                'user with username {username} already exists'
                ' (auth token {token})').format(
                    username=username,
                    token=existing_users.first().auth_token)
        else:
            user = User.objects.create_superuser(username, email, password)
            auth_token = Token.objects.create(user=user)
            print 'created superuser with auth_token {token}'.format(
                token=str(auth_token))


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0009_auto_20150429_1447'),
    ]

    operations = [
        migrations.RunPython(create_super_user)
    ]
