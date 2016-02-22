from django.core.management.base import BaseCommand

from postcode_api.models import CacheVersion


class Command(BaseCommand):
    args = 'latest_filename'

    def handle(self, *args, **options):
        latest_filename = None
        if len(args) == 1:
            latest_filename = args[0]

        cv = CacheVersion(last_addressbase_file=latest_filename)
        cv.save()
