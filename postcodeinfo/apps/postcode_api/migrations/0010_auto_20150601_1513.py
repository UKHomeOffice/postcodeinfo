# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from django.db import models, migrations

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

def create_super_user(apps, schema_editor):
    username = os.environ.get('PCI_DEFAULT_ADMIN_USER_USERNAME')
    email = os.environ.get('PCI_DEFAULT_ADMIN_USER_EMAIL')
    password = os.environ.get('PCI_DEFAULT_ADMIN_USER_PASSWORD')
    
    existing_users = User.objects.filter(username=username)

    if username == None:
      print 'skipping admin user creation - no defaults set (PCI_DEFAULT_ADMIN_USER_xyz)'
    else:
      if len(existing_users) == 0:
        user = User.objects.create_superuser(username, email, password)
        auth_token = Token.objects.create(user=user)
        print 'created superuser with auth_token %s' % str(auth_token)
      else:
        print 'user with username %s already exists' % username


class Migration(migrations.Migration):

    dependencies = [
        ('postcode_api', '0009_auto_20150429_1447'),
    ]

    operations = [
      migrations.RunPython(create_super_user)
    ]
