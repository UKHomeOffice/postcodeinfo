#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.db import transaction
from rest_framework.authtoken.models import Token


class Command(BaseCommand):

    help = 'create a non super user and token.'

    def add_arguments(self, parser):
        parser.add_argument('-u', '--username', required=True, help='username')
        parser.add_argument('-e', '--email', required=True, help='email')
        parser.add_argument('-p', '--password', required=True, help='password')
        # specify the token when we want to make the same token usable
        # on a second cluster
        parser.add_argument(
            '-t', '--token',
            help='token is optional. if not specified, it will be generated.')

    def handle(self, *args, **options):
        try:
            email = options['email']
            EmailValidator()(email)
        except ValidationError as exc:
            raise CommandError(exc)
        with transaction.atomic():
            try:
                user = User.objects.create_user(
                    options['username'],
                    email,
                    options['password'],
                    is_staff=True
                )
                user.save()
            except IntegrityError as exc:
                raise CommandError(exc)
            token = options.get('token')
            if token:
                t = Token(user_id=user.id, key=token)
            else:
                t = Token(user_id=user.id)
            t.save()
            msg = (
                'successfully create user(username="{}", email="{}")'
                ' with token "{}".'
            ).format(options['username'], email, t.key)
            self.stdout.write(self.style.SUCCESS(msg))
